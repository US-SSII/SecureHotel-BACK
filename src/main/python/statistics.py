from datetime import datetime
import os


def calculate_successful_ratio(total_messages, success_count):
    return (success_count / total_messages if total_messages > 0 else 0)*100*1.0

def get_report():
    logs_dir = "../logs/"
    reports_dir = "../reports/"
    evaluation = "../reports/evaluation.txt"
    
    now = datetime.now()
    
    pattern = "{:04d}-{:02d}".format(now.year, now.month)
        
    error_count = 0
    success_count = 0
    
    for file in os.listdir(logs_dir):
        if file.startswith(pattern):
            with open(os.path.join(logs_dir, file), "r") as log_file:
                for line in log_file:
                    if "ERROR" in line:
                        error_count += 1
                    elif "SUCCESS" in line:
                        success_count += 1
    
    with open(evaluation, "r") as evaluation_file:
        last_lines = evaluation_file.readlines()[-2:]
    
    previous_month_percentage = 0
    second_previous_month_percentage = 0
    
    for i, line in enumerate(last_lines):
        parts = line.split(" | ")
        if len(parts) == 2:
            if i == 0:
                previous_month_percentage = float(parts[2])
            if i == 1:
                second_previous_month_percentage = float(parts[2])
    
    eval = calculate_successful_ratio(success_count + error_count, success_count)
    
    report_name = f"Report-{pattern}.txt"
    report_file_path = os.path.join(reports_dir, report_name)

    with open(report_file_path, 'w', encoding='utf-8') as report_file:
        report_file.write("=" * 50 + "\n")
        report_file.write(f"Monthly Report - {pattern}\n")
        report_file.write("=" * 50 + "\n\n")
        report_file.write("Total messages: {}\n".format(error_count + success_count))
        report_file.write("Total successful messages: {}\n".format(success_count))
        report_file.write("Total error messages: {}\n\n".format(error_count))
        report_file.write("Percentage of complete messages: {}\n\n".format(eval))
        report_file.write("=" * 50)        
        
    if (eval > previous_month_percentage and eval > second_previous_month_percentage) or eval == previous_month_percentage:
        evolution = "+"
    elif eval < previous_month_percentage or eval < second_previous_month_percentage:
        evolution = "-"
    else:
        evolution = "0"
        
    with open(evaluation, "a") as evaluation_file:
        evaluation_file.write("{:s} | {:s} | {}\n".format(pattern, evolution, eval))