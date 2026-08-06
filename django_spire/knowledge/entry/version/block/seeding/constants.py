from __future__ import annotations

from django_spire.knowledge.entry.version.block.data.heading_data import HeadingEditorBlockData
from django_spire.knowledge.entry.version.block.data.list.choices import ListEditorBlockDataStyle
from django_spire.knowledge.entry.version.block.data.list.data import ListEditorBlockData
from django_spire.knowledge.entry.version.block.data.text_data import TextEditorBlockData


ONBOARDING_ARTICLE = [
    HeadingEditorBlockData(text='New Employee Onboarding', level=1),
    TextEditorBlockData(
        text='This guide walks new team members through their first week, from equipment setup to meeting your manager. '
        'It brings together everything you need to become productive quickly and connect with the people who will support you.'
    ),
    HeadingEditorBlockData(text='Before Your First Day', level=2),
    TextEditorBlockData(
        text='Your manager will reach out before your start date to confirm logistics, share the welcome agenda, and answer any questions. '
        'In the meantime, complete the paperwork sent to your personal email so payroll and benefits are ready on day one.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {
                'content': 'Confirm your start date and office location with your manager',
                'items': [],
            },
            {'content': 'Complete tax, payroll, and benefits forms', 'items': []},
            {'content': 'Add your personal email to your onboarding profile', 'items': []},
            {'content': 'Review the employee handbook in the HR collection', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Equipment and Access', level=2),
    TextEditorBlockData(
        text='IT provisions your laptop and accounts within your first two days. You will receive a company email address, a badge for office access, '
        'and VPN credentials if you work remotely. Do not share your password or badge with anyone.'
    ),
    TextEditorBlockData(
        text='If your equipment has not arrived after two days, raise a ticket with IT through the help desk and copy your manager. '
        'Equipment is provided based on your role and is yours for the duration of your employment.'
    ),
    HeadingEditorBlockData(text='First Week Checklist', level=2),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.CHECKLIST,
        items=[
            {
                'content': 'Set up your laptop and connect to the network',
                'meta': {'checked': False},
                'items': [],
            },
            {
                'content': 'Complete the security awareness training',
                'meta': {'checked': False},
                'items': [],
            },
            {
                'content': 'Meet your manager for a 1:1 and agree on goals',
                'meta': {'checked': False},
                'items': [],
            },
            {
                'content': 'Join the team channels for your department',
                'meta': {'checked': False},
                'items': [],
            },
            {
                'content': 'Book your 30-day check-in with HR',
                'meta': {'checked': False},
                'items': [],
            },
        ],
    ),
    HeadingEditorBlockData(text='Where to Get Help', level=2),
    TextEditorBlockData(
        text='HR is your primary contact for benefits, payroll, and policy questions. IT handles accounts, hardware, and software access. '
        'Your manager is the best first stop for questions about your role and team.'
    ),
    TextEditorBlockData(
        text='Keep this guide handy and reach out early if anything is unclear. A smooth onboarding sets '
        'you up for a strong start, and everyone on the team is happy to help.'
    ),
]

IT_SECURITY_ARTICLE = [
    HeadingEditorBlockData(text='IT and Security Policies', level=1),
    TextEditorBlockData(
        text='These policies protect company data, customer information, and the systems that keep our business running. '
        'Every employee is responsible for following them, and the security team can answer questions at any time.'
    ),
    HeadingEditorBlockData(text='Passwords and Accounts', level=2),
    TextEditorBlockData(
        text='Use unique, strong passwords for every account and enable two-factor authentication wherever it is offered. '
        'Never reuse a personal password for a company account, and do not write passwords down where others can see them.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Use a company-approved password manager', 'items': []},
            {'content': 'Enable two-factor authentication on all accounts', 'items': []},
            {'content': 'Report suspected compromise to IT within the hour', 'items': []},
            {'content': 'Never share your account with a colleague or vendor', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Email and Phishing', level=2),
    TextEditorBlockData(
        text='Phishing is the most common way attackers gain access. Beware of unexpected attachments, urgent requests, and links that do not '
        'match known domains. When in doubt, forward the message to the security team instead of clicking anything.'
    ),
    TextEditorBlockData(
        text='The security team runs regular simulated phishing tests. Failing a simulation is a learning opportunity, not a disciplinary matter; '
        'reporting suspicions is always encouraged.'
    ),
    HeadingEditorBlockData(text='Data Classification and Handling', level=2),
    TextEditorBlockData(
        text='Data is classified as public, internal, or confidential. Public data can be shared externally. Internal data is for employees only. '
        'Confidential data, such as customer records and financial information, requires extra protection and must not be stored on personal devices.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Use the approved secure vault for confidential documents', 'items': []},
            {'content': 'Encrypt confidential files before sending them by email', 'items': []},
            {'content': 'Lock your screen whenever you leave your desk', 'items': []},
            {
                'content': 'Shred or securely delete confidential documents you no longer need',
                'items': [],
            },
        ],
    ),
    HeadingEditorBlockData(text='Incident Reporting', level=2),
    TextEditorBlockData(
        text='If you lose a device, see suspicious activity, or believe data may have been exposed, report it immediately. '
        'Early reporting limits damage and is treated confidentially.'
    ),
]

REMOTE_WORK_ARTICLE = [
    HeadingEditorBlockData(text='Remote and Hybrid Work', level=1),
    TextEditorBlockData(
        text='This policy outlines expectations for team members who work remotely, whether fully remote, hybrid, or occasionally from home. '
        'It is meant to give you flexibility while keeping collaboration and productivity strong.'
    ),
    HeadingEditorBlockData(text='Work Hours and Availability', level=2),
    TextEditorBlockData(
        text='Most roles operate on a flexible schedule within core collaboration hours. Agree on availability with your manager, '
        'and keep your calendar current so teammates know when to reach you.'
    ),
    HeadingEditorBlockData(text='Setting Up Your Workspace', level=2),
    TextEditorBlockData(
        text='Choose a quiet, well-lit space with a stable internet connection. Use a headset for calls to reduce background noise. '
        'If you need equipment such as a monitor, webcam, or ergonomic chair, request it through IT.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Use a wired connection or strong Wi-Fi for calls', 'items': []},
            {'content': 'Keep your workspace free from distractions', 'items': []},
            {'content': 'Take scheduled breaks to protect your wellbeing', 'items': []},
            {'content': 'Test your camera and microphone before meetings', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Communication Norms', level=2),
    TextEditorBlockData(
        text='Default to asynchronous communication for updates and questions. Use video for team meetings and important 1:1s, '
        "and set expectations for response times with your team. Recording meetings is only permitted with everyone's consent."
    ),
    TextEditorBlockData(
        text='When you are off work, respect your own boundaries and those of others. Messages sent outside working hours can wait until the next day '
        'unless they are marked urgent.'
    ),
    HeadingEditorBlockData(text='Travel and Reimbursement', level=2),
    TextEditorBlockData(
        text='Your manager approves any travel before you book. Submit expense reports within thirty days using the expense tool, '
        'and attach receipts for every claim.'
    ),
]

HR_POLICIES_ARTICLE = [
    HeadingEditorBlockData(text='HR Policies and Employee Handbook', level=1),
    TextEditorBlockData(
        text='The handbook sets out the rules, expectations, and benefits that shape working life at the company. '
        'It applies to all employees and is reviewed annually, so check back for updates.'
    ),
    HeadingEditorBlockData(text='Code of Conduct', level=2),
    TextEditorBlockData(
        text='We expect honesty, respect, and fairness in every interaction. Harassment, discrimination, and retaliation are not tolerated '
        'in any form, and all reports are investigated confidentially.'
    ),
    HeadingEditorBlockData(text='Paid Time Off', level=2),
    TextEditorBlockData(
        text='Full-time employees accrue paid time off each pay period. Submit time-off requests through the HR tool at least two weeks in advance '
        'and receive manager approval before making travel plans.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.ORDERED,
        meta={'start': 1},
        items=[
            {
                'content': 'Open the HR tool and request your dates',
                'items': [],
                'meta': {'start': 1},
            },
            {'content': 'Add your manager as an approver', 'items': [], 'meta': {'start': 1}},
            {
                'content': 'Set an out-of-office message for your email',
                'items': [],
                'meta': {'start': 1},
            },
            {
                'content': 'Hand off critical tasks to a colleague',
                'items': [],
                'meta': {'start': 1},
            },
        ],
    ),
    HeadingEditorBlockData(text='Leaves of Absence', level=2),
    TextEditorBlockData(
        text='Medical, family, and personal leaves are available to eligible employees. Speak with HR early, even if you are unsure of your '
        'eligibility, so we can guide you through the process and protect your role.'
    ),
    TextEditorBlockData(
        text='All leave-related conversations are kept confidential and are used only to support your needs and comply with applicable law.'
    ),
    HeadingEditorBlockData(text='Resignation and Offboarding', level=2),
    TextEditorBlockData(
        text='If you decide to leave, provide written notice to your manager and HR. We will hold an offboarding meeting to return equipment, '
        'recover access, and discuss final pay.'
    ),
]

BENEFITS_ARTICLE = [
    HeadingEditorBlockData(text='Employee Benefits', level=1),
    TextEditorBlockData(
        text='Our benefits package is designed to support your health, finances, and future. This guide explains what is available and how to enrol, '
        'so you can make the most of what the company offers.'
    ),
    HeadingEditorBlockData(text='Health and Dental Coverage', level=2),
    TextEditorBlockData(
        text='Eligible employees can enrol in medical, dental, and vision plans. Coverage starts on the first of the month after your '
        'enrolment is confirmed by HR. Dependants can be added at enrolment or during annual open enrolment.'
    ),
    HeadingEditorBlockData(text='Retirement and Savings', level=2),
    TextEditorBlockData(
        text='The company offers a retirement savings plan with an employer match. You control your contribution rate, and matching is applied '
        'to the first portion of your salary each pay period.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Choose your contribution rate in the benefits portal', 'items': []},
            {'content': 'Confirm your investment allocation', 'items': []},
            {'content': 'Review your match statement each quarter', 'items': []},
            {'content': 'Update beneficiaries after major life changes', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Wellness and Time Off', level=2),
    TextEditorBlockData(
        text='Wellness benefits include an annual allowance for fitness, mental health support, and a health spending account. '
        'Use the benefit to cover expenses that improve your wellbeing, from gym memberships to counselling sessions.'
    ),
    TextEditorBlockData(
        text='Paid time off, paid holidays, and paid parental leave are detailed in the HR policies. Contact the benefits team for '
        'eligibility details and any questions about your specific situation.'
    ),
    HeadingEditorBlockData(text='How to Enrol', level=2),
    TextEditorBlockData(
        text='New hires enrol within the first thirty days. Visit the benefits portal, review the available plans, and submit your choices. '
        'HR confirms enrolment and answers questions at any point during the year.'
    ),
]

SALES_ARTICLE = [
    HeadingEditorBlockData(text='Sales Process and Best Practices', level=1),
    TextEditorBlockData(
        text='This guide describes the standard sales process, from prospecting to closing. Following it consistently helps our team move deals '
        'forward efficiently and keeps our pipeline accurate.'
    ),
    HeadingEditorBlockData(text='The Sales Stages', level=2),
    TextEditorBlockData(
        text='Every opportunity moves through defined stages. Logging an accurate stage matters more than moving fast, because it keeps forecasts '
        'reliable and makes it easy for teammates to pick up an account.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Qualify the account against our ideal customer profile', 'items': []},
            {'content': 'Identify the decision maker and budget owner', 'items': []},
            {'content': 'Run a discovery call to understand the need', 'items': []},
            {'content': 'Propose a tailored solution and pricing', 'items': []},
            {'content': 'Negotiate and close the deal', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Discovery Calls', level=2),
    TextEditorBlockData(
        text="Discovery is about listening more than talking. Ask open questions about the customer's goals, challenges, and timeline, "
        'and take notes directly into the CRM so nothing is lost.'
    ),
    TextEditorBlockData(
        text='A good discovery call ends with a clear next step, such as a product demo or a follow-up with the technical team. '
        'Always confirm the decision-making process before investing more time.'
    ),
    HeadingEditorBlockData(text='Proposals and Pricing', level=2),
    TextEditorBlockData(
        text='Use the approved proposal template and pricing guidance. Obtain the necessary approvals before sharing a proposal, '
        'and be clear about what is included, payment terms, and the validity period of the quote.'
    ),
    HeadingEditorBlockData(text='Managing Your Pipeline', level=2),
    TextEditorBlockData(
        text='Keep every account current. Update stages weekly, log calls and emails, and flag any deal that has stalled for more than two weeks '
        'so leadership can help unblock it.'
    ),
]

MARKETING_ARTICLE = [
    HeadingEditorBlockData(text='Marketing Guidelines', level=1),
    TextEditorBlockData(
        text='These guidelines ensure our marketing is consistent, accurate, and on brand across every channel. '
        'They apply to campaigns, social media, email, and external communications.'
    ),
    HeadingEditorBlockData(text='Brand Voice and Tone', level=2),
    TextEditorBlockData(
        text='Our brand is clear, helpful, and confident. Write in plain language, avoid jargon, and put the customer first. '
        'Always check spelling and grammar before anything goes live.'
    ),
    HeadingEditorBlockData(text='Approving Campaigns', level=2),
    TextEditorBlockData(
        text='All external campaigns require review by the marketing lead and, where relevant, legal and compliance. '
        'Allow at least three business days for approvals and do not bypass the review workflow.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Use the approved brand assets and templates', 'items': []},
            {'content': 'Include required disclaimers and unsubscribe links', 'items': []},
            {'content': 'Verify claims and statistics before publishing', 'items': []},
            {'content': 'Route sensitive campaigns through legal review', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Social Media', level=2),
    TextEditorBlockData(
        text='When posting on company channels, follow the content calendar and coordinate with the marketing team. '
        'Customer information must never be shared without consent, and responses to complaints should be handled calmly and privately.'
    ),
    TextEditorBlockData(
        text='If a post receives unexpected attention or negative feedback, pause and loop in the marketing lead before responding further.'
    ),
    HeadingEditorBlockData(text='Measuring Success', level=2),
    TextEditorBlockData(
        text='Agree on goals and metrics before launching a campaign. Review performance after the campaign and document what worked '
        'so future efforts build on real results.'
    ),
]

PROJECT_MANAGEMENT_ARTICLE = [
    HeadingEditorBlockData(text='Project Management Standards', level=1),
    TextEditorBlockData(
        text='These standards describe how projects are planned, tracked, and delivered across the company. '
        'Following a common approach keeps stakeholders informed and helps teams finish on time and on budget.'
    ),
    HeadingEditorBlockData(text='Planning a Project', level=2),
    TextEditorBlockData(
        text='Every project starts with a clear charter that defines the goal, scope, stakeholders, and success criteria. '
        'Secure sign-off from the sponsor before committing resources.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.ORDERED,
        meta={'start': 1},
        items=[
            {'content': 'Write and approve the project charter', 'items': [], 'meta': {'start': 1}},
            {
                'content': 'Break the work into milestones and tasks',
                'items': [],
                'meta': {'start': 1},
            },
            {'content': 'Estimate effort and assign owners', 'items': [], 'meta': {'start': 1}},
            {
                'content': 'Agree on reporting cadence with stakeholders',
                'items': [],
                'meta': {'start': 1},
            },
        ],
    ),
    HeadingEditorBlockData(text='Tracking and Reporting', level=2),
    TextEditorBlockData(
        text='Update the project tracker at least weekly with progress, risks, and decisions. Reports should state the current status clearly and '
        'call out anything that needs attention rather than burying it in detail.'
    ),
    TextEditorBlockData(
        text='Maintain a risk register and review it in every status meeting. Assign an owner to each open risk and a date to review or close it.'
    ),
    HeadingEditorBlockData(text='When Things Go Off Track', level=2),
    TextEditorBlockData(
        text='If a project slips, escalate early with options rather than surprises. Present the impact, the root cause, and at least two '
        'recovery choices so the sponsor can decide quickly.'
    ),
    HeadingEditorBlockData(text='Closing a Project', level=2),
    TextEditorBlockData(
        text='A finished project should be formally closed with a lessons-learned review. Capture what went well and what to improve, '
        'and archive the documentation so future teams can reference it.'
    ),
]

CUSTOMER_SUPPORT_ARTICLE = [
    HeadingEditorBlockData(text='Customer Support Standards', level=1),
    TextEditorBlockData(
        text='Our support team is the voice of the company for customers. These standards help us resolve issues quickly, '
        'communicate clearly, and keep customers informed at every step.'
    ),
    HeadingEditorBlockData(text='Response and Resolution', level=2),
    TextEditorBlockData(
        text='Acknowledge every new ticket within one business hour and set a clear expectation for when the issue will be resolved. '
        'If a fix will take longer than promised, update the customer before the deadline passes.'
    ),
    HeadingEditorBlockData(text='Communication Best Practices', level=2),
    TextEditorBlockData(
        text='Write in simple, direct language and avoid technical jargon unless the customer is technical. Confirm the problem in your own words '
        'before proposing a fix, and always close the loop once the issue is resolved.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Confirm the exact error and impact', 'items': []},
            {'content': 'Reproduce the issue if possible', 'items': []},
            {'content': 'Apply the documented solution', 'items': []},
            {'content': 'Verify with the customer before closing', 'items': []},
            {'content': 'Log any new workaround for future reference', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Escalation', level=2),
    TextEditorBlockData(
        text='Escalate when a customer is at risk, an issue affects multiple accounts, or a resolution requires another team. '
        'Include the full context so the receiving team can act without repeating the investigation.'
    ),
    TextEditorBlockData(
        text='Keep the customer informed throughout an escalation and make sure the handover is smooth, with a named point of contact.'
    ),
    HeadingEditorBlockData(text='Knowledge Base Use', level=2),
    TextEditorBlockData(
        text='Search the knowledge base before starting an investigation. When you resolve a novel issue, document the solution so the '
        'next person resolves it faster and the customer experience stays consistent.'
    ),
]

TRAVEL_EXPENSE_ARTICLE = [
    HeadingEditorBlockData(text='Travel and Expense Policy', level=1),
    TextEditorBlockData(
        text='This policy explains how to book business travel and claim expenses. It is designed to be fair to employees '
        'while keeping spending within budget.'
    ),
    HeadingEditorBlockData(text='Booking Travel', level=2),
    TextEditorBlockData(
        text='Book flights, hotels, and car rentals through the approved travel tool to access negotiated rates. '
        'Make bookings as far in advance as possible and choose the most cost-effective reasonable option.'
    ),
    HeadingEditorBlockData(text='Approvals', level=2),
    TextEditorBlockData(
        text='Travel requires manager approval before booking. Unapproved travel may not be reimbursed, so confirm your business need '
        'and budget before making commitments.'
    ),
    ListEditorBlockData(
        style=ListEditorBlockDataStyle.UNORDERED,
        items=[
            {'content': 'Obtain manager approval before booking', 'items': []},
            {'content': 'Use the approved travel tool where possible', 'items': []},
            {'content': 'Keep all receipts for every expense', 'items': []},
            {'content': 'Submit claims within thirty days', 'items': []},
        ],
    ),
    HeadingEditorBlockData(text='Expense Categories', level=2),
    TextEditorBlockData(
        text='Reimbursable expenses include transport, accommodation, meals, and business essentials such as internet and printing. '
        'Personal items and upgrades beyond the standard rate are not reimbursed.'
    ),
    TextEditorBlockData(
        text='If a receipt is lost, you may submit a declaration in the expense tool explaining the expense. These declarations are reviewed by finance.'
    ),
    HeadingEditorBlockData(text='Submitting a Claim', level=2),
    TextEditorBlockData(
        text='Create your expense report shortly after the trip, attach receipts, and route it to your manager and finance for approval. '
        'Reimbursement is issued on the next scheduled payroll cycle after approval.'
    ),
]


KB_ARTICLES = [
    ONBOARDING_ARTICLE,
    IT_SECURITY_ARTICLE,
    REMOTE_WORK_ARTICLE,
    HR_POLICIES_ARTICLE,
    BENEFITS_ARTICLE,
    SALES_ARTICLE,
    MARKETING_ARTICLE,
    PROJECT_MANAGEMENT_ARTICLE,
    CUSTOMER_SUPPORT_ARTICLE,
    TRAVEL_EXPENSE_ARTICLE,
]
