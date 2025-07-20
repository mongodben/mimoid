#### INDUSTRY

Education

#### PRODUCTS

MongoDB Atlas  
MongoDB Online Archive

#### USE CASE

Content Management

#### CUSTOMER SINCE

2020

**INTRODUCTION**

# Educating 2.4 million students across Brazil

Cogna Educação (Cogna) is a leading educational organization in Brazil. It’s made up of a group of institutions with the shared ethos of changing lives through education. Founded over 50 years ago, Cogna’s 25,000+ employees serve more than 2.4 million students across B2B and B2C markets. The company also generates more than R$439 million through social programs and activities, which enables them to transform over 2,000 Brazilian communities.

Cogna’s comprehensive portfolio of services puts the student journey at the center of all their decisions. By offering flexible and customizable solutions for every stage of the educational journey, it has the capacity to impact up to 22 million students. The organization offers partial and full scholarships at private colleges under the government-assisted ‘University for All Program’, known as Prouni. Students can also apply for the Student Financing Fund, FIES, to secure funding for their studies.

Cogna is proud to play a role in stimulating lifelong learning. Whether you are two years old or 100 years old, in the classroom or in the workplace, Cogna believes there are always opportunities to learn, evolve, and improve the way things are done.

“Our pioneering spirit goes well beyond education and into the realm of technology,” says Eduardo Chavarria, technology manager at Cogna. “Cogna empowers its tech teams to experiment, fail fast, and move forward. We innovate to retain our position as a market leader by helping staff and students find the best version of themselves.”

**THE CHALLENGE**

## Handling seasonal peaks in funding applications

Prospective students, once pre-approved by the FIES or Prouni program, will be able to send their documents for analysis through Cogna’s self-service portal. Every semester, this portal receives huge spikes in traffic. Up to 57,000 applicants submit forms per cycle and 22 supporting documents per person over a couple of weeks. Once submitted, applicants are automatically assigned a protocol number to identify them and help track the progress of their submission.

These are then reviewed by a team of dedicated finance and operational staff who verify the documents are accurate. These teams keep in touch with applicants through the portal at every stage, and communicate with the relevant competent government entities to provide scholarships or funding.

“The self-service portal needs to be highly available. Any outage or loss of data could mean applicants have to start again and risks delaying the scholarship awarding process,” explained Danilo Vicentini, technology manager and solutions architect at Cogna. “Our legacy on-premises platform lacked scalability, which caused latency issues and bottlenecks,” he added. “We operate in a regulated industry and can be penalized with hefty fines if we’re responsible for people missing out on funding. It was in everyone’s interests to migrate the platform to a more stable and robust architecture that we could tailor to create a great user experience.”

During peak times, the IT team spun up war rooms to quickly address any dips in performance. But the limited scalability of the system was causing two to three seconds of latency per click, making for a poor applicant experience.

“We had issues with the hardware, memory, and CPU. We decided to move the portal to a database platform in the cloud to improve performance and make it easier to manage peak times,” said Chavarria.

**THE SOLUTION**

## Migrating the application portal to the cloud

Cogna started researching the best database platform to support its applicant portal. While carrying out their due diligence, Cogna discovered that other education institutions, as well as other areas of their own business, highly recommended MongoDB Atlas.The team decided to implement MongoDB Atlas on Microsoft Azure and migrate workloads from the on-premises solution into the cloud.

“We decided to use Microsoft Azure because we had the right connectors to get up and running in a very short period,” said Chavarria, referring to Azure’s Application Gateway and Load Balancer connectors. “Our environment had ‘collapsed’ at that point, so we needed to get up and running quickly,” he continued.

There are five Cogna applications running on MongoDB. In addition to the self-service portal, there’s an authentication tool, and apps to manage approvals, workflows, reports, and documents. Bots automatically migrate records to the company’s document management system when applicants are approved and enrolled as students.

**“With MongoDB, the application process is seamless and reliable. Every completed application we receive is an opportunity to give someone a better education and level the playing field for students who need funding to get there.”**  

Eduardo Chavarria, Technology Manager, Cogna Educação

With support from the local MongoDB team in Brazil, Cogna used the mongomirror, mongodump, mongorestore methods to streamline the migration. This allowed for a smooth and efficient document transfer, protecting data quality and consistency. Databases and collections that required more attention were carefully analyzed and validated, while uncurated data was moved faster. In total, ten databases were migrated and 370 gigabytes of data consolidated down to 79 gigabytes.

MongoDB Atlas provides Cogna a comprehensive non-relational database management solution. It’s also easy to add on additional products and capabilities, such as Online Archive, as required.

Cogna uses MongoDB Atlas indexes to improve performance and Online Archive to implement tiered storage. “We have a huge volume of data, which drives up storage costs and impacts performance,” said Vicentini. “We configured the platform to automatically migrate data of a certain age to the online archive. That means we have the data we need for audits, but it’s accessed by a different connector to keep our live database fast and lean.”

The team uses the platform’s out-of-the-box monitoring tools and alerts to make sure the environment is running smoothly. This has eliminated the need for war rooms, as even during peak times MongoDB autoscales to accommodate the surge in demand without manual input. Cogna also receives email alerts from MongoDB Atlas, and is currently implementing monitoring and alerts in its observability platform, Datadog.

**THE RESULTS**

## A portal that’s fast and always available

Since implementing MongoDB Atlas, Cogna has achieved 100% availability and six millisecond latency on its applications portal. It now takes seconds, rather than minutes, to submit an application, which accelerates the whole document analysis process. Staff can review documents faster and get applications approved for benefits so the student can start planning the next steps in their education. The portal also has the potential to scale, keeping up with business growth.

**“We swapped a system with timeout issues to one with a 200-millisecond response time. My team no longer has to worry about database maintenance, we know it’s reliable and everything will work during peaks.”**  

Danilo Vicentini, Technology Manager and Solutions Architect, Cogna Educação

Between the support from MongoDB teams, and Atlas’ highly performant, scalable, and cost-effective solution, Cogna is confident about its future. As it plans the upcoming migration of its on-premises workloads to Atlas, Cogna looks forward to replicating its success and the great results it achieved with Prouni and FIES.

## What will your story be?

#### MongoDB will help you find the best solution.

Get Started