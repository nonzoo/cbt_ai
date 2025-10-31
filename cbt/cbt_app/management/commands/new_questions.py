from django.core.management.base import BaseCommand
from cbt_app.models import Exam, Question

class Command(BaseCommand):
    help = "Seed the database with a Cloud Computing exam and 10 sample questions"

    def handle(self, *args, **options):
        # Create the Exam
        exam, created = Exam.objects.get_or_create(
            name="Cloud Computing",
            defaults={"duration_minutes": 60}
        )

        if not created:
            self.stdout.write(self.style.WARNING("Exam 'Cloud Computing' already exists."))
        else:
            self.stdout.write(self.style.SUCCESS("Exam 'Cloud Computing' created."))

        # Sample Questions
        questions = [
            {
                "text": "What is the main advantage of cloud computing?",
                "option1": "High maintenance cost",
                "option2": "Scalability and flexibility",
                "option3": "Manual resource allocation",
                "option4": "Offline data access only",
                "correct_option": 2,
                "difficulty": 1,
                "topic": "Introduction to Cloud Computing"
            },
            {
                "text": "Which of the following is an example of IaaS?",
                "option1": "Google Docs",
                "option2": "Dropbox",
                "option3": "Amazon EC2",
                "option4": "Salesforce",
                "correct_option": 3,
                "difficulty": 1,
                "topic": "Cloud Service Models"
            },
            {
                "text": "What does PaaS stand for?",
                "option1": "Platform as a Service",
                "option2": "Protocol as a System",
                "option3": "Program as a Service",
                "option4": "Platform and Storage",
                "correct_option": 1,
                "difficulty": 1,
                "topic": "Cloud Service Models"
            },
            {
                "text": "Which company provides the Azure cloud platform?",
                "option1": "Google",
                "option2": "Microsoft",
                "option3": "Amazon",
                "option4": "IBM",
                "correct_option": 2,
                "difficulty": 1,
                "topic": "Cloud Providers"
            },
            {
                "text": "Which of the following is NOT a deployment model of cloud computing?",
                "option1": "Public Cloud",
                "option2": "Private Cloud",
                "option3": "Hybrid Cloud",
                "option4": "Personal Cloud",
                "correct_option": 4,
                "difficulty": 2,
                "topic": "Deployment Models"
            },
            {
                "text": "What is virtualization in cloud computing?",
                "option1": "Physical networking of computers",
                "option2": "Creation of virtual resources like servers and storage",
                "option3": "Storing data offline",
                "option4": "Encrypting user data",
                "correct_option": 2,
                "difficulty": 2,
                "topic": "Virtualization"
            },
            {
                "text": "Which of these is an example of SaaS?",
                "option1": "Microsoft Office 365",
                "option2": "Amazon EC2",
                "option3": "Google Cloud Engine",
                "option4": "VMware vSphere",
                "correct_option": 1,
                "difficulty": 2,
                "topic": "Cloud Service Models"
            },
            {
                "text": "Which protocol is most used for secure communication in cloud environments?",
                "option1": "HTTP",
                "option2": "FTP",
                "option3": "HTTPS",
                "option4": "SMTP",
                "correct_option": 3,
                "difficulty": 3,
                "topic": "Security"
            },
            {
                "text": "Which of the following ensures data availability in cloud systems?",
                "option1": "Load balancing and redundancy",
                "option2": "Manual backup only",
                "option3": "Single point of failure",
                "option4": "Low bandwidth connection",
                "correct_option": 1,
                "difficulty": 3,
                "topic": "Reliability"
            },
            {
                "text": "What is the pay-as-you-go model in cloud computing?",
                "option1": "Paying for all resources upfront",
                "option2": "Paying only for resources used",
                "option3": "Free access to all services",
                "option4": "Fixed monthly payment regardless of usage",
                "correct_option": 2,
                "difficulty": 2,
                "topic": "Billing Model"
            },
        ]

        # Check if questions already exist
        existing_count = Question.objects.filter(exam=exam).count()
        if existing_count >= 10:
            self.stdout.write(self.style.WARNING("Questions already exist for this exam."))
            return

        # Add questions
        Question.objects.bulk_create([
            Question(exam=exam, **q) for q in questions
        ])

        self.stdout.write(self.style.SUCCESS("10 questions for 'Cloud Computing' added successfully!"))
