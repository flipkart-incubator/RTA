from utilities.csv_to_pie import pie_chart_maker
from utilities.make_domains_list import domain_list

domains = domain_list("./input_files/domains.txt")
for domain in domains:
    pie_chart_maker("./"+domain+"/tools/Port_scan/csv_file.csv", "./"+domain+"/tools/Port_scan/pie_chart.png", "./utilities/vulnerable_ports.csv")
