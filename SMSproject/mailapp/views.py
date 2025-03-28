from django.shortcuts import render
import pandas as pd


import re
from django.core.mail import EmailMessage
from django.conf import settings

# Create your views here.

all_valid=False
def home(request):
    global all_valid
    global df
    
    def is_valid_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, str(email)))
    def cal_percentage(total,attended):
        return round((attended/total)*100)
    def Ststus_bat(n):
        filled = "⭐" * (n // 20)  # Each ⭐ represents 20%  
        empty = "☆" * (5 - (n // 20))  # Empty stars for remaining  
        return filled + empty 
        
    Form=False
    
    
    if request.method == 'POST' and request.FILES.get('file'):
        Form=True
        uploaded_file = request.FILES['file']

        # Read the Excel file directly without saving
        df = pd.read_excel(uploaded_file)
        
        df['Status'] = df['Email'].apply(lambda x: is_valid_email(x))
        if df['Status'].all(): #Check all mails are valid or not
            all_valid=True
        df=df.to_dict(orient="records")



        # Convert DataFrame to HTML (for testing output)s
        
        
        return render(request,'home.html',{"df":df,"Form":Form,'all_valid':all_valid})
    if request.method == 'POST'and not request.FILES.get('file'):
        Form=False 
        if all_valid:
            
            for student in df:
                student_name=student['Name']
                student_mail=student['Email']
                Lab_Attend,Total_Lab= map(int, student['Lab_Attdence'].strip().replace("'", "").split('/'))
                Mock_Attended=student["Mock_Attended"]
                Mock_Performance=student['Mock_Performance']
                Test_Attended=student["Test_Attended"]
                Test_Performance=student['Test_Performance']
                Assignments_Submitted=student['Assignments']
                Lab_Percentage=cal_percentage(int(Total_Lab),int(Lab_Attend))
                Mock_Percentage=cal_percentage(int(20),int(Mock_Performance))
                Test_percentage=cal_percentage(20,int(Test_Performance))
                Assignment_Percentage=cal_percentage(4,int(Assignments_Submitted))
                
                score=(Lab_Percentage+Mock_Percentage+Test_percentage+Assignment_Percentage)//4
                if score >= 90:
                    remark = f"Excellent Performance! You have achieved an impressive overall score of {score}%. 🎉 Your dedication and consistency are commendable. Keep up the great effort, and continue excelling! 🚀"
                elif score >= 75:
                    remark = f"Great Effort! Your overall score stands at {score}%. 👍 You're on the right track, but there’s still room for improvement. Keep refining your skills and aim for excellence! 💯"
                elif score >= 50:
                    remark = f"Good Attempt! You have secured {score}% overall. 💪 Stay consistent, focus on weaker areas, and practice more to improve your performance. 🚀"
                else:
                    remark = f"Needs Improvement! Your overall score is {score}%. 🌱 Learning is a journey, and every step counts. Identify areas where you can improve, seek guidance, and keep practicing! You’ve got this! 🔥"

                    
                email_body = f"""
                    <html>
                    <body>
                        
                        <p>Greeting's From </p><h4>VCUBE SOFTWARE SOLUTIONS</h4>
                        <h4>📊 Monthly Performance Report</h4>
                        <p>Dear {student_name},</p>
                        <p>We hope you are doing well! Below is your monthly performance summary at VCUBE SOFTWARE SOLUTIONS</p>
                        <table border="1" cellspacing="0" cellpadding="10">
                            <tr>
                                <th>Category's</th>
                                <th>Total Sessions</th>
                                <th>Sessions Attended</th>
                                <th>Performance Score</th>
                                <th>Rating</th>
                            </tr>
                            <tr>
                                <th>Lab</th>
                                <td style="text-align: center;">{Total_Lab}</td>
                                <td style="text-align: center;">{Lab_Attend}</td>
                                <td style="text-align: center;">{Lab_Percentage}%</td>
                                <td style="text-align: center;">{Ststus_bat(Lab_Percentage)}</td>
                            </tr>
                            <tr>
                                <th>Mock Interview</th>
                                <td style="text-align: center;">{4}</td>
                                <td style="text-align: center;">{Mock_Attended}</td>
                                <td style="text-align: center;">{Mock_Percentage}%</td>
                                <td style="text-align: center;">{Ststus_bat(Mock_Percentage)}</td>
                            </tr>
                            <tr>
                                <th>Weekly Test</th>
                                <td style="text-align: center;">{4}</td>
                                <td style="text-align: center;">{Test_Attended}</td>
                                <td style="text-align: center;">{Test_percentage}%</td>
                                <td style="text-align: center;">{Ststus_bat(Test_percentage)}</td>
                            </tr>
                            <tr>
                                <th>Weekly Assignments</th>
                                <td style="text-align: center;">{4}</td>
                                <td style="text-align: center;">{Assignments_Submitted}</td>
                                <td style="text-align: center;">{Assignment_Percentage}%</td>
                                <td style="text-align: center;">{Ststus_bat(Assignment_Percentage)}</td>
                            </tr>
                        
                            
                        
                        </table>
                        <p><strong>Overall Rating:</strong>{Ststus_bat(score)}</p>
                        <p><strong>Overall Remark:</strong> {remark}</p>
                        
                        <p><b>Best Regards</b>,<br>Team Vcube </p>
                    </body>
                    </html>
                    """ 
            
                subject = "📊 Your Monthly Performance Report"
                
                message = EmailMessage(subject, email_body, settings.EMAIL_HOST_USER, [student_mail])
                message.content_subtype = "html"  # Ensure content type is HTML
            
                message.send() 
                print("e-mail sent ")    
        
    return render(request,'home.html',{"Form":Form})