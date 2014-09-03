import arcpy, numpy
	
def score(mean, sd, stat):
	temp_score = 0
	if stat >= mean - sd and stat <= mean + sd:
		temp_score = 1
	if stat >= mean + sd:
		temp_score = 2
	return temp_score

def score_field(name):
	return name + '_SCR'

# Required to test values because numpy.nanmean not available until numpy 1.8
def is_numeric(num):
	try:
		float(num)
	except (ValueError, TypeError):
		return False
	else:
		return True
	
inlyr = arcpy.GetParameterAsText(0)
fields = arcpy.GetParameterAsText(1)

field_array = fields.split(';')

stat_store = {}

# Calculate stats
for f in field_array:
	stat_store[f] = {}
	search_cursor = arcpy.SearchCursor(inlyr)
	stat_array = []
	for row in search_cursor:
		if is_numeric(row.getValue(f)):
			stat_array.append(row.getValue(f))
	m = numpy.mean(stat_array)
	stat_store[f]['mean'] = m
	s = numpy.std(stat_array)
	stat_store[f]['std'] = s

# Score stats	
for f in field_array:
	# Add score field
	new_field = score_field(f)
	arcpy.AddField_management(inlyr, new_field, 'SHORT')
	# Score field values based on mean and std dev
	update_cursor = arcpy.UpdateCursor(inlyr)
	for row in update_cursor:
		scored = score(stat_store[f]['mean'], stat_store[f]['std'], row.getValue(f))
		row.setValue(new_field, scored)
		update_cursor.updateRow(row)
	del update_cursor

# Field name for aggregated score
final_score_field = 'FINALSCORE'

# 	
arcpy.AddField_management(inlyr, final_score_field, 'SHORT')
final_cursor = arcpy.UpdateCursor(inlyr)
for row in final_cursor:
	final_score_val = 0
	for f in field_array:
		final_score_val = final_score_val + row.getValue(score_field(f))
	row.setValue(final_score_field, final_score_val)
	final_cursor.updateRow(row)
	
del final_cursor
arcpy.AddMessage(stat_store)