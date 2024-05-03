

---

## SECTION 1 : PROJECT TITLE
## CinePaw AI - Explore the world of movies with your own personalised movie guide!

<img src="Images/front.webp" width="400" />  

---

## SECTION 2 : EXECUTIVE SUMMARY / PAPER ABSTRACT
#### Problem Statement and Proposed Solution 

The current streaming platforms recommender systems often fail to capture individual preferences and lack personalisation elements in providing movie recommendation. This may lead to loss of users over a period of time once they feel frustrated and hop to another platform that give them better user experience to find the movies that interest them.  

Thus, our proposal - CinePaw AI introduces an advanced movie recommendation system that leverages Large Language Models (LLMs) to create an intelligent, interactive chatbot to retain the users and make them royal to our platforms. This chatbot goes beyond traditional recommendation algorithms by engaging in natural language dialogues with users, enabling a personalized movie discovery experience and improve the overall user experience in sourcing for movies that they are interested and stay royal to the platform. 

 

#### Differentiation from Existing Markets 

CinePaw AI differentiates itself from existing market offerings such as  

its recommender model (ComiRec), which provides nuanced recommendations by categorising user interests into multiple segments.  

chatbot that remembers and reference past user interactions. This stateful interaction enhances the personalization and relevance of recommendations.  

cognitive services, allowing users to engage in human-like conversations with the system, receiving both spoken and textual responses, setting it apart from the conventional, less interactive recommendation services found in current streaming platforms. 

 

#### Market Positioning 

The streaming service market is highly competitive and continuously evolving with viewers seeking more personalized and engaging experiences. We position CinePaw AI to be the forefront in shifting towards the direction what we define as Interactive User-Centric Recommendation System (IUCRS). It fills a significant gap left by existing platforms, offering unique experience that emphasises on user interaction, engagement, and satisfaction. 

 

#### Conclusion and Future Prospects 

Moving forward, CinePaw AI plans to expand its data sources and enhance its ecosystem to maintain relevance and adapt to changing market demands. The project team is also aware of potential challenges, such as data source limitations and the need for continuous updates to the AI algorithms to handle diverse user interactions. These enhancements will be crucial for scaling operations and improving the system's accuracy and more precise user engagement. 

---

## SECTION 3 : CREDITS / PROJECT CONTRIBUTION

| Official Full Name  | Student ID | Work Items | Email  |
| :------------ |:---------------:| :-----| :-----|
| Tan Eng Hui | A0291201W | Ideation, Architecture/Design, Testing, Front/Backend Development, Landscape Exploration, Knowledge Sharing, Project Documentation| e1330340@u.nus.edu |
| Lois Chee Li Ping | A0292098R | Ideation, Architecture/Design, Testing, Front/Backend Development, Landscape Exploration, Knowledge Sharing, Project Documentation| e1338192@u.nus.edu |
| Dong Yuantong | A0292041N |Ideation, Architecture/Design, Testing, Front/Backend Development, Landscape Exploration, Knowledge Sharing, Project Documentation| e1337515@u.nus.edu |
| Wang Tao | A0291189R | Ideation, Architecture/Design, Testing, Front/Backend Development, Landscape Exploration, Knowledge Sharing, Project Documentation| e1330328@u.nus.edu |

---

## SECTION 4 : VIDEO OF USE CASE DEMO AND TECHNICAL DESIGN 

| Promo/Demo Video  | Technical Design video | 
| :------------ |:---------------:| 
| <a href="https://youtu.be/wNqYnHEz6jM"><img src="Images/salesmanbear.jpg" alt="CinePaw AI" width="200" height="200"></a> | <a href="https://youtu.be/5cxTfu4g51s">  <img src="Images/techbear.jpg" alt="CinePaw AI" width="200" height="200"></a> | 




---

## SECTION 5 : PROJECT REPORT

Refer to [Project Report.pdf](ProjectReport/Project%20Report.pdf) in the **ProjectReport** folder



---

## SECTION 6 : DEPLOYMENT AND USER GUIDE

You can also refer to **Installation/Deployment Guide** and **User Guide** respectively at appendix section in [Project Report.pdf](ProjectReport/Project%20Report.pdf). 


**Pre-requisites**
- Clone/download the repository from [IRS-PM-2024-01-13-ISO6PT-GRP-Cinepaw-AI](https://github.com/eng-hui/IRS-PM-2024-01-13-ISO6PT-GRP-Cinepaw-AI).  
Ensure you obtain the following API keys from the listed resources:
  - [OpenAI Platform](https://platform.openai.com/)
  - [The Movie Database (TMDB)](https://www.themoviedb.org/)
  - [Azure AI Speech Services](https://azure.microsoft.com/en-us/products/ai-services/ai-speech)
- Docker
- Internet Access
- Chrome Browser

**Instruction for Environmental variables and API access tokens**
1.	Modify the .env file in the backend folder and update the following keys with your own keys (refer to pre-requisite)

| Key                   | Default Value/Source                       |
|-----------------------|--------------------------------------------|
| DEFAULT_LLM_ENDPOINT  | openai or azure_openai                     |
| DEFAULT_MODEL         | gpt-4-turbo-preview                        |
| OPENAI_API_ENDPOINT   | # can be empty if not azure openai         |
| OPENAI_API_KEY        | [According to the OpenAI service]          |
| AZURESPEECH_API_KEY   | [According to the Azure AI speech service] |
| TMDB_API              | [API Key_According to the TMDB API service]|

Format reference: [https://www.dotenv.org/docs/security/env.html](https://www.dotenv.org/docs/security/env.html)

<img src="Images/env_var.png" />

**Instruction for Docker deployment**  
2.  Launch terminal from the SystemCode folder  
3.  Run `docker build . -f docker/dockerfile -t=cinepaw`  to build a cinepaw docker image  
<img src="Images/docker_build.png" />  

4.  Run cinepaw image by `docker run -p 8111:9880 --name cinepaw cinepaw`  
<img src="Images/docker_run.png" />  
 
5.  Launch browser and navigate to http://localhost:8111 to start using cinepaw*  
*Do take note that it will take a while to warm up the system, if no response from the chatbot, please refresh after a few seconds.  
<img src="Images/webpage_launch.png" />  


---
