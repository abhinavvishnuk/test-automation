import xml.etree.ElementTree as ET 
from datetime import datetime

#function to get elapsed time
def get_elapsed_time(s1, s2, FMT):
	tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
	return str(tdelta)[:-3]

def get_total_statistics(node):
	total = int(node.get('pass')) + int(node.get('fail'))
	pass_percentage = round(int(node.get('pass')) * 100/total, 2)
	fail_percentage = round(100.00 - pass_percentage, 2)
	return [str(total), str(pass_percentage), str(fail_percentage)]

def update_total_statistics_card(node):
	total, pass_percentage, fail_percentage = get_total_statistics(node)
	return html_template_code.replace('replace-total',total,  1)\
	.replace('replace-pass', critical_test.get('pass'), 1)\
	.replace('replace-fail', critical_test.get('fail'), 1)\
	.replace('replace-pass-percentage', pass_percentage, 2)\
	.replace('replace-fail-percentage', fail_percentage, 2)
	

def get_suite_statistics(suite):
	stat = root.find(suite_statistics.format(suite.get('id')))
	status = suite.find('status')
	total, pass_percentage, fail_percentage = get_total_statistics(stat)
	elapsed_time = get_elapsed_time(status.get('starttime'),status.get('endtime'),time_format)
	return """<tr>
			<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>
           	<td><div class='percentage'><span class='percentage-pass' style='width:{}%'></span></div></td>
            <td>{}</td>
    </tr>""".format(suite.get('name'), total, stat.get('pass'), stat.get('fail'), elapsed_time, pass_percentage, pass_percentage )


#variables to set report tree level and output.xml file path
report_level = 1
output_xml = '/home/chinju/dev/venvs/output.xml'
time_format = '%Y%m%d %H:%M:%S.%f'

print('Generating report...')

#open and read template html code for report
f = open('/opt/lampp/htdocs/sample/report.html','r')
html_template_code = f.read()
f.close()

#parsing output.xml
tree = ET.parse(output_xml) 
root = tree.getroot() 

#Get Summary Information
suite = root.find("suite/status")
elapsed_time= get_elapsed_time(suite.get('starttime'), suite.get('endtime'), time_format)
status_message = 'All test passed'

#Get Total Statistics
critical_test = root.find("statistics/total/stat[1]")
all_test = root.find("statistics/total/stat[2]")

if(suite.get('status') != 'PASS'):
	if(critical_test.get('fail') == 1):
		status_message = '1 critical test failed'
	else:
		status_message = critical_test.get('fail') + ' critical tests failed'


#update summary information in report
html_template_code = html_template_code.replace('replace-summary-place-holder', status_message, 1)\
.replace('replace-summary-place-holder', suite.get('status').lower(), 1)\
.replace('replace-summary-place-holder', suite.get('starttime'), 1)\
.replace('replace-summary-place-holder', suite.get('endtime'), 1)\
.replace('replace-summary-place-holder', elapsed_time, 1)

#update critical test statistics in report
html_template_code = update_total_statistics_card(critical_test)

#update all test statistics in report
html_template_code = update_total_statistics_card(all_test)

#Generate suite level report
i = 0
suite_level = "suite"
while (i < report_level):
	i += 1
	suite_level += "/suite"

suite_statistics = "statistics/suite/stat[@id='{}']"
table_rows = ""
for suite in root.findall(suite_level):
	table_rows += get_suite_statistics(suite)

html_template_code = html_template_code.replace('replace-with-table-rows', table_rows, 1)

f = open('mp-automation-report.html','w')
f.write(html_template_code)
f.close()


print('Report generated.')
