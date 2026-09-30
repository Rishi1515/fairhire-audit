# Resumes to score

Score each resume against both jobs in its family before looking at any model result, the review sheet or the design notes, so the scores stay blind. Levels: 0 no evidence, 1 mentioned only, 2 applied, 3 applied with depth and a stated outcome. A skill that appears only in the skills list is at most 1.

## Rubrics

### DA-01 Data Analyst, Retail Operations

- `sql` SQL querying (weight 0.25): Wrote queries that join several tables or aggregate large datasets. Built recurring data extracts or reports from a database. Improved query speed or correctness.
- `spreadsheet_analysis` Spreadsheet analysis (weight 0.15): Built pivot-table or lookup-based analysis used by others. Automated a manual spreadsheet report.
- `dashboarding` Dashboarding and BI (weight 0.20): Built or maintained a dashboard that others used regularly. States who used the dashboard or what decision it supported.
- `statistical_reasoning` Statistical reasoning and forecasting (weight 0.15): Explained differences between actual and forecast values. Applied a statistical method (trend, regression, test) to a business question.
- `data_quality` Data cleaning and quality (weight 0.10): Found and fixed missing, duplicated or inconsistent records. Set up checks that catch data errors.
- `stakeholder_communication` Stakeholder communication (weight 0.15): Presented findings or recommendations to store, operations or supply chain managers. Wrote reports, notes or documentation read by non-specialists. Changed a decision or process as a result of the analysis.

### DA-02 Product Data Analyst

- `sql` SQL on event data (weight 0.25): Wrote SQL on event or transaction data, including window functions. Built datasets used for product analysis.
- `experimentation` Experiment design and analysis (weight 0.20): Designed or analysed an A/B test and reported the result. Considered sample size, duration or significance. Stated limits of an experiment result.
- `product_metrics` Product metrics (weight 0.20): Defined or tracked funnel, activation or retention metrics. Ran cohort or funnel analysis.
- `python_analysis` Python or R for analysis (weight 0.10): Used Python or R to clean, analyse or model data in a described task.
- `dashboarding` Dashboarding (weight 0.10): Built a dashboard that a product or business team used.
- `stakeholder_communication` Stakeholder communication (weight 0.15): Presented findings or recommendations to product managers, designers or business teams. Wrote reports, notes or documentation read by non-specialists. Changed a decision or process as a result of the analysis.

### MA-01 Performance Marketing Analyst

- `paid_media` Paid media platforms (weight 0.20): Managed or analysed paid campaigns on named platforms. States budget, scale or results.
- `funnel_attribution` Funnel and attribution analysis (weight 0.20): Analysed the path from click to purchase. Set up or audited tracking or attribution.
- `campaign_testing` Campaign testing (weight 0.15): Designed or analysed a campaign test and reported the result.
- `data_tools` SQL and spreadsheets (weight 0.15): Used SQL or spreadsheets to combine and analyse marketing data.
- `budget_optimisation` Budget and efficiency optimisation (weight 0.15): Recommended or made budget changes based on efficiency metrics. States the effect on cost or return.
- `reporting_dashboards` Reporting dashboards (weight 0.10): Built or maintained marketing performance reports used by others.
- `stakeholder_communication` Stakeholder communication (weight 0.05): Presented campaign results or recommendations to marketers or managers.

### MA-02 CRM and Customer Insights Analyst

- `customer_segmentation` Customer segmentation (weight 0.20): Built customer segments from behaviour or value data. Segments were used for campaigns or decisions.
- `retention_analysis` Retention and lifetime value (weight 0.20): Analysed churn, retention or lifetime value by cohort or segment.
- `crm_platforms` CRM and campaign platforms (weight 0.15): Planned, ran or measured campaigns in a CRM or email platform.
- `data_tools` SQL, spreadsheets or Python (weight 0.20): Used SQL, spreadsheets or Python to prepare and analyse customer data.
- `survey_research` Survey and customer research (weight 0.10): Designed or analysed customer surveys or interviews.
- `insight_storytelling` Insight storytelling (weight 0.15): Presented customer insights with recommendations. Insight led to a change in a campaign or offer.

### SE-01 Backend Software Engineer

- `backend_language` Backend programming language (weight 0.20): Built production features or services in a backend language. Owned a service or module.
- `api_design` API design and development (weight 0.20): Designed or built APIs used by other teams or customers. Handled versioning, validation or errors in an API.
- `relational_databases` Relational databases (weight 0.15): Designed schemas or wrote migrations. Improved query performance with indexes or query changes.
- `automated_testing` Automated testing (weight 0.15): Wrote unit or integration tests for their own code. Improved test reliability or coverage.
- `cloud_deployment` Containers, cloud and CI/CD (weight 0.15): Deployed services using containers or a CI/CD pipeline. Worked with cloud infrastructure.
- `production_debugging` Production support and debugging (weight 0.10): Investigated and fixed production issues. Took part in on-call or incident reviews.
- `collaboration` Code review and collaboration (weight 0.05): Reviewed others' code, wrote design documents or mentored engineers.

### SE-02 Frontend Engineer

- `javascript_typescript` JavaScript and TypeScript (weight 0.20): Built production features in JavaScript or TypeScript. Introduced or maintained typed code.
- `react` React (weight 0.20): Built or maintained React applications in production. Designed reusable components.
- `accessibility_responsive` Accessibility and responsive design (weight 0.15): Made interfaces meet an accessibility standard or fixed accessibility issues. Built layouts that work across screen sizes.
- `frontend_testing` Frontend testing (weight 0.15): Wrote component or end-to-end tests. Set up or improved a frontend test suite.
- `api_integration` API integration and state (weight 0.15): Connected interfaces to REST or GraphQL APIs. Managed client-side data or state.
- `web_performance` Web performance (weight 0.10): Measured and improved load time or bundle size.
- `design_collaboration` Design collaboration (weight 0.05): Worked with designers or contributed to a design system.

## Resumes

### DA-R06 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Senior data analyst with seven years of experience in e-commerce and healthcare operations. Leads forecasting, dashboarding and experiment analysis for operations and product teams.

EXPERIENCE
Senior Data Analyst, Katong Market Online | Singapore | Feb 2022 - Present
- Lead analysis for the seller operations and checkout teams, covering about 2 million monthly orders.
- Built and maintain Tableau dashboards on stock availability, delivery times and checkout conversion, used by 60 managers in operations and product.
- Write and review Snowflake SQL, including window functions, for weekly forecasting and funnel datasets.
- Designed and analysed A/B tests on checkout changes with power calculations and agreed success metrics; one test raised checkout conversion by 1.8 percentage points.
- Built a Python demand forecast for the top 500 products that cut stock-outs by 12% in pilot categories.
- Present quarterly insights to the operations and product leadership teams.

Data Analyst, Novena Clinic Group | Singapore | Jul 2019 - Jan 2022
- Built Power BI dashboards on clinic waiting times and patient volumes for 20 clinic managers.
- Wrote SQL Server queries combining appointment and billing data.
- Set up data quality checks that reduced errors in the monthly management pack.

EDUCATION
Bachelor of Science (Honours) in Statistics, GPA 4.2 / 5.0
National University of Singapore | Aug 2015 - Jun 2019
Relevant coursework: Regression Analysis, Time Series Analysis, Design of Experiments

SKILLS
Data: SQL (Snowflake, SQL Server), Python (pandas, statsmodels), Excel
Visualisation: Tableau, Power BI
Methods: Forecasting, A/B testing, Regression
```

### SE-R07 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Mobile engineer with five years of experience building Android apps and the backend services behind them.

EXPERIENCE
Mobile Engineer, Geylang Eats | Singapore | Feb 2023 - Present
- Build Android app features in Kotlin for about 200,000 monthly users.
- Built two backend services in Kotlin with Spring Boot that provide REST APIs for order tracking.
- Designed MySQL tables for order status history.
- Write unit tests with JUnit and set up the app's GitHub Actions build pipeline.

Android Developer, Yishun Games Studio | Singapore | Aug 2021 - Jan 2023
- Built Android game menus and in-app purchase screens in Kotlin.
- Fixed crashes found through Firebase Crashlytics reports.

EDUCATION
Bachelor of Engineering in Computer Science and Design, GPA 3.8 / 5.0
Singapore University of Technology and Design | Sep 2017 - Aug 2021
Relevant coursework: Software Construction, Mobile Application Development

SKILLS
Languages: Kotlin, Java, SQL
Frameworks: Android, Spring Boot
Tools: MySQL, JUnit, GitHub Actions, Firebase
```

### DA-R03 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Operations executive moving into data analysis. Completed the Google Data Analytics Certificate and a personal project analysing public housing data with SQL and Tableau.

EXPERIENCE
Operations Executive, Jurong Event Rentals | Singapore | Jun 2024 - Present
- Update daily booking and equipment availability sheets in Google Sheets.
- Created a weekly equipment utilisation summary with pivot tables for the operations manager.
- Schedule deliveries and collections for about 25 events a week.

Customer Service Associate, Bedok Mobile Store | Singapore | Jan 2023 - May 2024
- Resolved customer questions on mobile plans and device orders.
- Tracked daily store sales against targets in a shared spreadsheet.

Projects
- HDB resale price analysis: Used SQLite and Tableau Public to analyse ten years of public HDB resale transactions and published a dashboard of price trends by town.

EDUCATION
Bachelor of Arts in Economics, GPA 3.4 / 5.0
Nanyang Technological University | Aug 2018 - Jun 2022
Relevant coursework: Introductory Econometrics, Statistics

SKILLS
Tools: Google Sheets, Excel, SQL (basic), Tableau Public
Certifications
- Google Data Analytics Professional Certificate (2024)
```

### SE-R05 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Frontend engineer with five years of experience building accessible React interfaces for health and media products.

EXPERIENCE
Frontend Engineer, Kembangan Health Tech | Singapore | Apr 2023 - Present
- Build patient booking and records screens in React and TypeScript, used by about 50,000 patients a month.
- Led an accessibility review against WCAG 2.1 AA and fixed over 120 issues, including screen reader labels and keyboard navigation.
- Write component tests with Jest and React Testing Library, and end-to-end tests with Playwright.
- Integrate with GraphQL APIs using Apollo Client.
- Wrote a small Node.js service that combines two backend APIs for the booking screen.

Frontend Developer, Holland Village Media | Singapore | Jun 2021 - Mar 2023
- Built responsive news pages in React for mobile and desktop.
- Reduced homepage bundle size by 35% with code splitting and lazy loading of images.
- Worked with designers in Figma to build a shared component library in Storybook.

EDUCATION
Bachelor of Engineering in Computer Science, GPA 3.9 / 5.0
Nanyang Technological University | Aug 2017 - May 2021
Relevant coursework: Human Computer Interaction, Web Application Design

SKILLS
Languages: TypeScript, JavaScript, HTML, CSS
Frameworks: React, Next.js, Node.js
Testing: Jest, React Testing Library, Playwright
Tools: GraphQL, Apollo, Storybook, Figma
```

### SE-R06 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Senior frontend engineer with almost seven years of experience leading React teams for travel and marketing websites.

EXPERIENCE
Senior Frontend Engineer, Siloso Travel | Singapore | May 2022 - Present
- Lead a team of 4 frontend engineers building the booking site in React, TypeScript and Next.js.
- Improved mobile Largest Contentful Paint from 4.1 to 2.2 seconds by fixing image loading and server rendering.
- Set accessibility standards for the team and added automated axe checks to the CI pipeline.
- Introduced Cypress end-to-end tests for the checkout flow.
- Work with designers to maintain the design system in Figma and Storybook.

Frontend Developer, Clarke Quay Creative | Singapore | Jan 2020 - Apr 2022
- Built responsive marketing websites and campaign pages in JavaScript and React.
- Connected pages to REST APIs for content and forms.

EDUCATION
Bachelor of Computing in Information Systems, GPA 3.8 / 5.0
National University of Singapore | Aug 2015 - Dec 2019
Relevant coursework: Interaction Design, Web Programming

SKILLS
Languages: TypeScript, JavaScript, CSS
Frameworks: React, Next.js
Testing: Cypress, Jest
Tools: Lighthouse, Figma, Storybook
```

### MA-R03 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
CRM analyst with almost six years of experience in retail loyalty and email marketing.

EXPERIENCE
CRM Analyst, Eunos Fresh Mart | Singapore | Oct 2022 - Present
- Built RFM segments for 450,000 loyalty members in SQL and used them to target weekly offers.
- Analyse monthly cohort retention and churn; a win-back programme for lapsed members recovered about 8% of them within three months.
- Plan and measure email and app push campaigns in Braze, including holdout groups.
- Ran retargeting campaigns on Meta Ads for lapsed members and reported cost per reactivation.
- Present monthly customer insight reports to the marketing and category teams.

Marketing Executive, Changi Beauty House | Singapore | Jan 2021 - Sep 2022
- Sent weekly email campaigns in Klaviyo and reported open and click rates.
- Ran a customer satisfaction survey and summarised the results in Excel.

EDUCATION
Bachelor of Business Administration in Marketing, GPA 3.9 / 5.0
National University of Singapore | Aug 2016 - Jun 2020
Relevant coursework: Marketing Analytics, Customer Relationship Management

SKILLS
Platforms: Braze, Klaviyo, Meta Ads
Data: SQL, Excel, Tableau
Methods: RFM segmentation, Cohort analysis
```

### DA-R04 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Retail supervisor with nearly five years of retail experience, including three years leading store teams and handling daily sales reporting.

EXPERIENCE
Retail Supervisor, Tampines Fashion Outlet | Singapore | Apr 2023 - Present
- Supervise a team of 8 sales associates and prepare weekly staff rosters.
- Record daily sales and stock deliveries in the point-of-sale system and email a daily summary to the area manager.
- Trained new staff on customer service standards and store procedures.

Sales Associate, Orchard Shoe Gallery | Singapore | Jan 2022 - Mar 2023
- Served customers and processed sales and returns.
- Helped with monthly stock takes.

EDUCATION
Bachelor of Business in Marketing, GPA 3.2 / 5.0
Singapore University of Social Sciences | Jan 2018 - Dec 2021

SKILLS
Tools: Microsoft Excel (basic), Microsoft Word, Point-of-sale systems
Other: Team leadership, Customer service
```

### SE-R02 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Full stack engineer with almost five years of experience building Java services and React interfaces for insurance and retail systems.

EXPERIENCE
Full Stack Engineer, Raffles Place Insurance Digital | Singapore | Jun 2023 - Present
- Build Java Spring Boot services and REST APIs for the online claims system, used by about 30,000 customers a month.
- Designed PostgreSQL schemas for claims data and wrote Flyway database migrations.
- Write JUnit and integration tests, and set up contract tests between frontend and backend.
- Build React and TypeScript screens for the claims form and connect them to the REST APIs.
- Deploy with Docker and Kubernetes on Azure through a Jenkins CI/CD pipeline.

Software Engineer, Bishan Retail Systems | Singapore | Jan 2022 - May 2023
- Built Java REST APIs for a point-of-sale back office.
- Fixed production issues found through logging and on-call support.
- Built React components for the store manager dashboard and wrote Jest tests for them.

EDUCATION
Bachelor of Computing in Computer Science, GPA 4.0 / 5.0
National University of Singapore | Aug 2017 - Dec 2021
Relevant coursework: Software Engineering, Database Systems, Web Development

SKILLS
Languages: Java, TypeScript, SQL
Frameworks: Spring Boot, React
Infrastructure: PostgreSQL, Docker, Kubernetes, Azure, Jenkins
Testing: JUnit, Jest
```

### DA-R07 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Product analyst with under two years of experience in education technology. Works with SQL, Python and dashboards to track how learners use the app.

EXPERIENCE
Product Analyst, Punggol Learning Labs | Singapore | Mar 2025 - Present
- Track weekly active users and lesson completion funnels in Metabase dashboards.
- Analysed 3 A/B tests on reminder notifications with a senior analyst, including checking whether sample sizes were large enough.
- Write PostgreSQL queries on event tables and analyse results in Python (pandas).
- Share short weekly notes on product metrics with the product manager.

Data Analytics Intern, Changi Travel Deals | Singapore | Jun 2024 - Dec 2024
- Cleaned booking data in Python and built charts for the marketing team.
- Wrote simple SQL queries to count bookings by channel.

EDUCATION
Bachelor of Science (Honours) in Mathematical Sciences, GPA 3.9 / 5.0
Nanyang Technological University | Aug 2020 - May 2024
Relevant coursework: Probability, Statistical Inference, Data Structures

SKILLS
Data: SQL (PostgreSQL), Python (pandas, SciPy), Excel
Visualisation: Metabase
```

### SE-R08 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
QA automation engineer with five years of experience testing web applications, moving towards frontend development.

EXPERIENCE
QA Automation Engineer, Buona Vista Software | Singapore | Mar 2023 - Present
- Build and maintain end-to-end test suites in Playwright and TypeScript for a web HR system, covering about 400 test cases.
- Built an internal React dashboard that shows test results and flaky tests for the engineering team.
- Added accessibility checks with axe to the test suite and reported issues to developers.
- Run the test suites in the GitHub Actions CI pipeline.

QA Engineer, Farrer Park Tech | Singapore | Sep 2021 - Feb 2023
- Wrote Cypress tests for a React web app and tested pages at different screen sizes.
- Reported and tracked bugs in Jira.

EDUCATION
Bachelor of Science (Honours) in Information and Communications Technology, GPA 3.7 / 5.0
Singapore Institute of Technology | Sep 2017 - Aug 2021
Relevant coursework: Software Testing, Web Programming

SKILLS
Languages: TypeScript, JavaScript
Testing: Playwright, Cypress, axe
Tools: React (basic), GitHub Actions, Jira
```

### SE-R04 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Junior web developer who moved into software after four years in logistics. Builds small Django web apps for local businesses.

EXPERIENCE
Junior Web Developer, Simei Digital Agency | Singapore | Mar 2025 - Present
- Build small websites and booking tools for local businesses using Django and Bootstrap.
- Add simple REST endpoints for mobile-friendly booking forms.
- Fix layout bugs on mobile screens using CSS and JavaScript.

Logistics Coordinator, Pioneer Freight Forwarding | Singapore | Jan 2021 - Jun 2024
- Coordinated bookings and documents for about 40 shipments a week.
- Built Excel macros that sped up the weekly shipment report.

Projects
- Hawker queue tracker: Django and PostgreSQL web app that shows queue times from user reports, with pytest tests.

EDUCATION
Bachelor of Science in Logistics and Supply Chain Management, GPA 3.5 / 5.0
Singapore University of Social Sciences | Jul 2016 - Jun 2020

SKILLS
Languages: Python, JavaScript, HTML, CSS
Frameworks: Django, Bootstrap
Tools: PostgreSQL (basic), Git
Certifications
- Full Stack Web Development Bootcamp, 24-week programme (2024)
```

### DA-R01 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Data analyst with five years of experience in retail and logistics reporting. Builds SQL data sets and Power BI dashboards used by operations managers, and explains forecast gaps in plain language.

EXPERIENCE
Data Analyst, Sembawang Mart | Singapore | Mar 2023 - Present
- Built and maintain 12 Power BI dashboards on store sales, stock availability and waste, used weekly by 40 store and category managers.
- Wrote BigQuery SQL joining sales, inventory and supplier tables to create a daily stock-out report, saving about 6 hours of manual reporting a week.
- Analyse weekly sales against forecast and present the main causes of variances above 10% at the monthly supply chain review.
- Built a seasonal trend and regression model in Python to adjust promotion forecasts, lowering average forecast error for promoted items from 24% to 17%.
- Set up automated validation checks that flag duplicate and missing transaction records before dashboards refresh.

Junior Data Analyst, Straits Parcel Logistics | Singapore | Jul 2021 - Feb 2023
- Produced delivery performance reports for 5 regional hubs in Excel using pivot tables and XLOOKUP.
- Wrote PostgreSQL queries to track late deliveries by route and driver shift.
- Reconciled delivery records between the courier app and the billing system, resolving about 300 mismatches a month.
- Ran a two-week trial of a new route-planning rule and summarised the change in on-time delivery for hub managers.

EDUCATION
Bachelor of Science (Honours) in Applied Statistics, GPA 4.1 / 5.0
Singapore Institute of Technology | Sep 2017 - Jun 2021
Relevant coursework: Regression Analysis, Time Series Forecasting, Database Systems

SKILLS
Data: SQL (BigQuery, PostgreSQL), Python (pandas, statsmodels), Excel
Visualisation: Power BI, Tableau
Methods: Forecasting, Regression, Variance analysis
Certifications
- Microsoft Certified: Power BI Data Analyst Associate
```

### MA-R01 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Performance marketing analyst with five years of experience in online retail across Singapore and Malaysia.

EXPERIENCE
Performance Marketing Analyst, Lavender Street Apparel | Singapore | Jan 2023 - Present
- Analyse Google Ads, Meta Ads and TikTok Ads campaigns with a monthly budget of about SGD 250,000.
- Built GA4 and UTM tracking checks and fixed conversion tracking gaps that had under-reported sales by about 15%.
- Designed creative tests and a geographic holdout test showing paid social drove about 20% more orders than last-click reports suggested.
- Recommend weekly budget shifts based on ROAS and CPA; moved 18% of spend to better-performing campaigns in 2025.
- Maintain Looker Studio dashboards for channel managers and present monthly results to the head of marketing.

Digital Marketing Analyst, Rochor Electronics Online | Singapore | Jul 2021 - Dec 2022
- Pulled campaign and order data with BigQuery SQL and combined it in Google Sheets.
- Reported weekly conversion funnel performance from Google Analytics.
- Ran A/B tests on landing pages with the web team.

EDUCATION
Bachelor of Business in Marketing, GPA 3.9 / 5.0
Nanyang Technological University | Aug 2017 - Jun 2021
Relevant coursework: Marketing Analytics, Consumer Behaviour

SKILLS
Platforms: Google Ads, Meta Ads, TikTok Ads, GA4
Data: SQL (BigQuery), Google Sheets, Looker Studio
```

### DA-R02 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Business analyst with four years of experience in operations reporting for banking and distribution. Strong in Excel and Power BI, with growing SQL skills.

EXPERIENCE
Operations Reporting Analyst, Marina Harbour Bank | Singapore | Jan 2024 - Present
- Maintain weekly and monthly operations reports in Excel for the retail banking service team, using pivot tables, XLOOKUP and Power Query.
- Built 4 Power BI dashboards tracking branch queue times and service requests, used by 15 branch managers.
- Write SQL Server queries to extract service request data, mostly single-table filters and groupings.
- Explain month-on-month changes in service levels to the operations manager, including a staffing recommendation for two branches.

Business Operations Executive, Clementi Health Supplies | Singapore | Jul 2022 - Dec 2023
- Prepared weekly sales and inventory summaries in Excel for the sales director.
- Cleaned the product master list, removing about 1,200 duplicate item codes.
- Worked with the warehouse team to investigate stock count differences.

EDUCATION
Bachelor of Business Administration in Operations Management, minor in Business Analytics, GPA 3.8 / 5.0
National University of Singapore | Aug 2018 - Jun 2022
Relevant coursework: Business Analytics, Statistics for Business, Database Management

SKILLS
Tools: Excel (advanced), Power Query, Power BI, SQL Server (basic)
Methods: Descriptive statistics, Variance analysis
```

### SE-R03 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Software engineer with four years of experience maintaining Java applications for banking and government clients.

EXPERIENCE
Software Engineer, Esplanade Commercial Bank | Singapore | Sep 2023 - Present
- Maintain Java services for internal loan processing, adding new fields and business rules.
- Build REST API endpoints used by the branch loan application.
- Write SQL queries and stored procedures in Oracle.
- Write JUnit tests for new code.

Associate Software Engineer, Boon Lay IT Services | Singapore | Jul 2022 - Aug 2023
- Supported Java applications for public sector clients, fixing bugs reported by users.
- Wrote SQL scripts to correct data issues.

EDUCATION
Bachelor of Engineering in Computer Engineering, GPA 3.6 / 5.0
Nanyang Technological University | Aug 2018 - Jun 2022
Relevant coursework: Object Oriented Programming, Database Systems

SKILLS
Languages: Java, SQL
Frameworks: Spring
Tools: Oracle Database, JUnit, Git
```

### MA-R08 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Sales executive with six years of experience in industrial and retail sales.

EXPERIENCE
Sales Executive, Tuas Industrial Supplies | Singapore | Mar 2022 - Present
- Sell safety equipment to construction and shipyard customers, meeting quarterly sales targets.
- Visit about 15 customers a week and record orders in the company CRM.
- Prepare quotations in Excel.

Retail Sales Associate, Jurong West Sports Outlet | Singapore | Sep 2020 - Feb 2022
- Served customers and handled product displays.
- Helped with stock counts.

EDUCATION
Bachelor of Arts in Sociology, GPA 3.4 / 5.0
Nanyang Technological University | Aug 2016 - Jun 2020

SKILLS
Tools: Excel, Microsoft Office
Other: B2B sales, Customer relationship management
```

### MA-R04 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Customer insights analyst with six years of experience in telecoms and market research.

EXPERIENCE
Customer Insights Analyst, Kranji Mobile | Singapore | Apr 2022 - Present
- Built customer segments with k-means clustering in Python on usage and billing data for 1.1 million subscribers.
- Analysed churn drivers by cohort and built a customer lifetime value model used to set retention offer budgets.
- Design quarterly NPS surveys in Qualtrics and link the results to usage data.
- Present insight reports with recommendations to marketing and customer experience teams; two recommendations changed the retention offer structure in 2024.
- Work with the CRM team to measure email campaigns sent through Salesforce Marketing Cloud.

Market Research Executive, Newton Research Partners | Singapore | Jul 2020 - Mar 2022
- Ran surveys and focus groups for consumer brands and wrote summary reports.
- Prepared survey data tables in SPSS and Excel.

EDUCATION
Bachelor of Science in Business Analytics, GPA 4.0 / 5.0
Singapore University of Social Sciences | Jul 2016 - Jun 2020
Relevant coursework: Data Mining, Marketing Research

SKILLS
Data: Python (pandas, scikit-learn), SQL, Excel, SPSS
Platforms: Qualtrics, Salesforce Marketing Cloud
```

### DA-R08 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
UX researcher with five years of experience in customer research and customer experience. Runs interviews, usability tests and surveys and turns them into recommendations for product teams.

EXPERIENCE
UX Researcher, Tiong Bahru Digital Studio | Singapore | Jan 2023 - Present
- Plan and run usability tests and customer interviews for banking and retail app clients.
- Worked with a client's analytics team to review A/B test results for a new sign-up flow, and explained interview findings about where users dropped off.
- Run surveys in Qualtrics and summarise the results in slide decks for product teams.
- Present research findings and recommendations to client product managers.

Customer Experience Executive, Queenstown Mobile Care | Singapore | Aug 2021 - Dec 2022
- Collected customer feedback and prepared monthly summaries of common complaints in Excel.
- Handled customer escalations for a team of 12.

EDUCATION
Bachelor of Science in Psychology, GPA 3.7 / 5.0
Singapore University of Social Sciences | Jul 2017 - Jun 2021
Relevant coursework: Research Methods, Statistics for Psychology

SKILLS
Research: Usability testing, Customer interviews, Survey design
Tools: Qualtrics, Figma, Excel
```

### MA-R06 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
CRM executive with five years of experience in email marketing for small retail brands.

EXPERIENCE
CRM Executive, Kovan Pet Supplies | Singapore | May 2023 - Present
- Plan and send weekly email campaigns in Klaviyo to about 80,000 subscribers.
- Split customers into groups by last purchase date and pet type for targeted emails.
- Track the repeat purchase rate of email customers in Excel and report it monthly.
- Ran a short customer survey in Google Forms about delivery preferences.

Marketing Assistant, Serangoon Garden Florist | Singapore | Sep 2021 - Apr 2023
- Sent monthly Mailchimp newsletters and updated the website.
- Helped run small Facebook ad campaigns for festive seasons.

EDUCATION
Bachelor of Business in Marketing, GPA 3.5 / 5.0
Singapore University of Social Sciences | Jul 2017 - Jun 2021

SKILLS
Platforms: Klaviyo, Mailchimp
Tools: Excel, Google Forms, Canva
```

### DA-R05 (score for DA-01 Data Analyst, Retail Operations, DA-02 Product Data Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Product analyst with five years of experience in consumer apps and online retail. Designs and analyses A/B tests and builds the product metrics that teams use to decide what to build.

EXPERIENCE
Product Analyst, Lalang Rides | Singapore | Aug 2023 - Present
- Defined activation and 30-day retention metrics for the driver app and built the weekly product metrics review in Looker.
- Designed and analysed 14 A/B tests on onboarding and pricing screens, including sample size planning and a written note on what each result could not show.
- Wrote BigQuery SQL on event tables, using window functions to build funnel and cohort datasets.
- Analysed onboarding funnel drop-off in Python (pandas) and recommended removing two steps; completion rose from 61% to 70% in the follow-up test.
- Present monthly findings to product managers and designers.

Junior Business Analyst, Serangoon Online Books | Singapore | Aug 2021 - Jul 2023
- Built weekly sales reports in Google Sheets and Looker Studio for the marketing team.
- Wrote MySQL queries on order and customer data.
- Checked daily order data for duplicates before reports were sent.

EDUCATION
Bachelor of Science in Business Analytics, GPA 4.0 / 5.0
Singapore University of Social Sciences | Jul 2017 - Jun 2021
Relevant coursework: Statistics, Database Systems, Experimental Design

SKILLS
Data: SQL (BigQuery, MySQL), Python (pandas, SciPy), Google Sheets
Visualisation: Looker, Looker Studio
Methods: A/B testing, Funnel and cohort analysis
```

### MA-R07 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Marketing coordinator with five years of experience in events and community marketing.

EXPERIENCE
Marketing Coordinator, Marine Parade Education Centre | Singapore | Feb 2023 - Present
- Organise open days and school roadshows, and track sign-ups in Excel.
- Run small Facebook and Instagram ad boosts for events and report reach and sign-ups.
- Send a monthly parent newsletter in Mailchimp.
- Collect feedback forms after events and summarise them for the centre manager.

Events Executive, Bedok Community Arts | Singapore | Jun 2021 - Jan 2023
- Coordinated community events with up to 500 attendees.
- Posted event updates on social media.

EDUCATION
Bachelor of Arts in English Language, GPA 3.7 / 5.0
National University of Singapore | Aug 2017 - May 2021

SKILLS
Tools: Excel, Mailchimp, Canva
Other: Event planning, Social media
```

### MA-R02 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Growth marketing lead with six years of experience in paid acquisition and customer analytics for consumer brands.

EXPERIENCE
Growth Marketing Lead, Upper Thomson Meals | Singapore | Sep 2022 - Present
- Lead paid search and paid social for a meal delivery brand with SGD 1.2 million annual media spend.
- Run incrementality tests with holdout regions to measure the true effect of Meta and Google campaigns.
- Built customer segments by order frequency and value in SQL, used to set different CAC targets for new and returning customers.
- Analysed cohort retention of customers from each channel and shifted budget toward channels with higher 90-day retention.
- Present quarterly growth reviews to the founders.

Marketing Analyst, Paya Lebar Fitness | Singapore | May 2020 - Aug 2022
- Reported Google Ads and Facebook Ads performance in Tableau.
- Ran email campaigns in HubSpot to bring back lapsed members.
- Used Excel and SQL to track cost per acquisition by channel.

EDUCATION
Bachelor of Business in Marketing, GPA 3.8 / 5.0
Singapore University of Social Sciences | Jul 2016 - Apr 2020

SKILLS
Platforms: Google Ads, Meta Ads, GA4, HubSpot
Data: SQL, Excel, Tableau
```

### SE-R01 (score for SE-01 Backend Software Engineer, SE-02 Frontend Engineer)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Backend software engineer with five years of experience building Python services for payments and logistics.

EXPERIENCE
Software Engineer, Tanjong Rhu Payments | Singapore | Jan 2023 - Present
- Design and build Python (FastAPI) services that handle settlement for about 9,000 merchants.
- Designed versioned REST APIs used by the mobile and partner teams, with input validation and clear error codes.
- Modelled PostgreSQL schemas and added indexes that cut the slowest report query from 40 seconds to 2 seconds.
- Write unit and integration tests with pytest; raised test coverage of the settlement service from 55% to 85%.
- Deploy with Docker and GitHub Actions to AWS ECS, and take part in on-call using Grafana and Prometheus alerts.
- Review code for 4 engineers and write design documents for new services.

Software Engineer, Ang Mo Kio Logistics Tech | Singapore | Jul 2021 - Dec 2022
- Built Django REST APIs for warehouse stock tracking.
- Wrote MySQL migrations and pytest tests for new features.
- Built simple internal admin pages with Django templates and some JavaScript.

EDUCATION
Bachelor of Engineering (Honours) in Software Engineering, GPA 4.1 / 5.0
Singapore Institute of Technology | Sep 2017 - Jun 2021
Relevant coursework: Distributed Systems, Database Systems, Software Testing

SKILLS
Languages: Python, SQL, JavaScript (basic)
Frameworks: FastAPI, Django
Infrastructure: PostgreSQL, MySQL, Docker, AWS, GitHub Actions, Grafana
Testing: pytest
```

### MA-R05 (score for MA-01 Performance Marketing Analyst, MA-02 CRM and Customer Insights Analyst)

```text
[Candidate]
+65 9000 0000 | Singapore

SUMMARY
Digital marketing executive with four years of experience running social media and paid ads for food and events businesses.

EXPERIENCE
Digital Marketing Executive, Bencoolen Bakes | Singapore | Jan 2024 - Present
- Run Meta Ads and Google Ads campaigns for a bakery chain with a monthly budget of about SGD 20,000.
- Track results in GA4 using UTM links and report cost per acquisition each week.
- Test two versions of ad creative each month and keep the one with the lower CPA.
- Update a weekly Google Sheets report for the marketing manager.

Social Media Executive, Dhoby Ghaut Events | Singapore | Jul 2022 - Dec 2023
- Planned Instagram and TikTok posts and tracked engagement.
- Boosted event posts on Facebook with small budgets.

EDUCATION
Bachelor of Arts in Communications and New Media, GPA 3.6 / 5.0
National University of Singapore | Aug 2018 - Jun 2022

SKILLS
Platforms: Meta Ads, Google Ads, GA4, Instagram, TikTok
Tools: Google Sheets, Canva
```
