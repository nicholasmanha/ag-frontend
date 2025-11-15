## **1\. Introduction**

### **1.1 Purpose**

The purpose of this document is to define the functional and non-functional requirements for the system (working title: **Agentic Dropshipping Agent**). This SRS will guide you (4-person team) in building a working prototype for your hackathon.

### **1.2 Scope**

This system will help e-commerce sellers (or you acting as pseudo-seller) by:

* Discovering trending / high-potential products (using Linkup)

* Recommending those products in a “Tinder-style” dashboard for sellers to accept/decline

* Automatically launching product campaigns (listing, marketing content) using AI agents

* Generating marketing content (videos, visuals) using Freepik for the influencer/market side

* Monitoring campaign performance and evolving strategy over time (self-evolving)

* Providing a dashboard UI (built using Lovable) where sellers can view actions, see product recs

* Managing workflows/integration using Airia

* Managing finance/tracking of campaigns via Campfire

### **1.3 Definitions, Acronyms, Abbreviations**

* Agentic: The system acts autonomously and adapts itself over time.

* Seller Dashboard: The frontend UI where a human “seller” interacts (views recommendations, accepts/declines).

* Campaign: A marketing/listing initiative for a specific product.

* Self-evolve: The system uses performance feedback (clicks, conversions, etc.) to adjust its strategy.

### **1.4 References**

* Standard SRS structure and best practices. ([GeeksforGeeks](https://www.geeksforgeeks.org/software-engineering/software-requirement-specification-srs-format/?utm_source=chatgpt.com))

* Hackathon criteria: agentic, self-evolving, using sponsor tools.

* Technology stack (to be detailed later).

---

## **2\. Overall Description**

### **2.1 Product Perspective**

This is a new system; it integrates with external services (product trend data, content creation tools, e-commerce listing APIs) and provides a unified dashboard for sellers.

### **2.2 Product Functions**

High-level list of what the system will do:

* Pull trending product data from Linkup.

* Score/rank products for “potential fit” (market volume, margin, novelty).

* Display product recommendations in a dashboard (swipe/accept/decline).

* On accept: automatically create listing \+ marketing campaign (generate copy, visuals, video) using Freepik and maybe other AI.

* Launch campaign and monitor performance metrics (views, clicks, conversions) — simulate if live data not available.

* Adapt future recommendations/listing strategy based on feedback (which campaigns succeeded, which failed).

* Provide UI for seller: track campaigns, see status

* Finance/tracking: log cost, revenue, margin using Campfire.

* Workflow orchestration: Airia manages agent steps (data fetch → score → recommendation → campaign launch → feedback → evolve).

### **2.3 User Classes and Characteristics**

* **Seller (Primary User)**: Has moderate technical skills, uses the dashboard to review product recs and monitor campaigns.

* **Admin/Team Member**: Your team managing the system (you may simulate).

* **System (Agent)**: Autonomous actor, not a direct user but central to logic.

* **Buyer (Indirectly)**: Person who wants to buy the products picked and advertised by the agent.

### **2.4 Operating Environment**

* Web-based dashboard (desktop).

* Backend services (local host for demo).

* Integrations with APIs (Linkup, Freepik, etc).

* Performance may be limited given hackathon timeframe.

### **2.5 Design & Implementation Constraints**

* Must integrate at least the announced sponsor tools (Linkup, Freepik, Airia, Campfire, Lovable).

* Time constraint: prototype in \~5 hours.

* Data may be simulated/mock if live APIs limited.

* Self-evolution logic must be visible in demo (even if simple).

* Dashboard must show clearly the agent’s actions, recs.

### **2.6 Assumptions and Dependencies**

* Access to APIs of external tools (or free/trial access).

* Ability to generate or simulate performance data.

* Internet connectivity.

* Basic hosting or local deployment available.

### **2.7 Technology Stack**

The system will be built using modern web and AI tools suitable for rapid prototyping in a hackathon context.

| **Layer**               | **Technology Options / Selected Tools**           | **Purpose**                                                                                |
| ----------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Frontend (UI)**       | **Lovable** (React-based) / TailwindCSS / Next.js | Seller dashboard with product recommendations, campaign views.          |
| **Backend / API**       | **FastAPI** (Python) or **Express.js** (Node.js)  | Core logic: connects product data, AI scoring, and workflows.                              |
| **Agent Workflow**      | **Airia** (sponsor tool)                          | Manages and logs multi-step agent actions (fetch → score → recommend → campaign → evolve). |
| **Product Data Source** | **Linkup API** (sponsor tool)                     | Fetches trending or high-potential products for recommendation.                            |
| **Content Generation**  | **Freepik API** (sponsor tool)                    | Generates visuals and ad creatives for campaigns.                                          |
| **Finance / Tracking**  | **Campfire** (sponsor tool)                       | Logs cost, revenue, and margin data for each campaign.                                     |
| **Database / Storage**  | SQLite / Supabase / Firebase                      | Store campaigns, metrics, and user data.                                                   |
| **AI / Scoring Logic**  | Python scripts (using NumPy/Pandas or OpenAI API) | Compute potential scores and self-evolve parameters.                                       |
| **Hosting / DevOps**    | Vercel / Render / Replit / Ngrok                  | Quick deployment and live demo hosting.                                                    |

Optional add-ons:

* **Authentication:** Firebase Auth / Lovable built-in auth
* **Real-time Updates:** WebSockets or periodic polling
* **Version Control:** GitHub (for team collaboration)

---

## **3\. Specific Requirements**

### **3.1 Functional Requirements**

Here are key functions with identifiers:

* **FR1**: The system shall fetch trending product data from Linkup at defined intervals (e.g., hourly).

* **FR2**: The system shall compute a “potential score” for each product based on market signals (e.g., demand, margin estimation).

* **FR3**: The system shall present product-recommendations to the seller in a Tinder-style swipe UI: accept or decline.

* **FR4**: If seller accepts a product, the system shall automatically generate listing copy (title, description) and marketing assets (image/video) using Freepik.

* **FR5**: The system shall launch a campaign and record performance metrics (views/clicks/conversions) into Campfire.

* **FR6**: The system shall monitor which campaigns succeed or fail and update its scoring algorithm/parameters (self-evolve) accordingly.

* **FR7**: The seller dashboard shall display agent actions (product recs, campaign launches, performance metrics) in real-time.

* **FR8**: The system shall allow manual override of agent decisions (seller can override product selection or campaign parameters).

* **FR9**: The workflow orchestration layer (Airia) shall log each step of the agent pipeline (data fetch → score → recommend → campaign → monitor → evolve).

### **3.2 Non-Functional Requirements**

* **Performance**: The system should generate a product recommendation within, e.g., 5 seconds of data fetch.

* **Usability**: The dashboard should be simple, intuitive (less than 3 clicks to accept product).

* **Scalability**: For prototype, system should handle at least 100 product candidates per hour.

* **Security**: Basic authentication for the seller dashboard (use Lovable for setup).

* **Maintainability**: Code modular to allow swapping of data sources or scoring logic.

* **Traceability**: Each campaign must store the decision path (why product recommended, what assets were generated).

### **3.3 Interface Requirements**

#### **3.3.1 User Interfaces**

* Login screen for seller.

* Main dashboard: product recommendations panel (swipe UI), recent campaigns list, performance metrics panel.

* Campaign detail screen: shows which product, listing copy, marketing asset preview, current performance stats, status.

* Settings screen: configure agent parameters (e.g., budget, number of products per cycle).

#### **3.3.2 Hardware Interfaces**

* Standard PC/laptop web browser (Chrome, Safari).

* No special hardware assumed.

#### **3.3.3 Software Interfaces**

* API to Linkup for product data (or mock).

* API or library to Freepik for asset generation.

* Database to store campaigns & metrics (e.g., SQLite, Postgres).

* Backend service for agent logic (could be Node/Python).

* Lovable UI library/integration.

* Airia workflow orchestration service.

* Campfire for financial/tracking data (or mock).

#### **3.3.4 Communications Interfaces**

* HTTPS for all API calls.

* Real-time updates on dashboard (WebSockets or polling) for campaign status.

### **3.4 Data Requirements**

* Product candidate dataset: product ID, name, category, historical demand metrics, estimate margin.

* Campaign records: product ID, listing info, date launched, status, performance metrics (views, clicks, conversions), budget, cost, revenue.

* Agent model parameters: scoring weights, historical performance aggregated.

* User (seller) profile: preferences, budget, manual overrides.

### **3.5 System Evolution Requirements**

Because the system itself evolves:

* Agent must log performance history and adjust scoring weights periodically (e.g., each campaign cycle).

* UI must show versioning or “strategy snapshot” (e.g., “Strategy version 1 → version 2” with improved performance).

* Keep track of agent decisions and outcomes to enable future “learning”.

---

## **4\. External Interface Requirements**

Already largely covered in section 3.3.

---

## **5\. Other Requirements**

### **5.1 Safety and Security**

* Authentication must prevent unauthorized access to seller dashboard.

* If using external APIs, credentials must be secured (no visible keys in UI).

### **5.2 Legal and Regulatory**

* The system will not recommend any banned or restricted products.

* Must provide transparency to seller: “agent recommended this product because…”.

### **5.3 Performance & Monitoring**

* Dashboard updates for campaign status should refresh within 2 seconds.

* Agent should handle at least one full campaign cycle (recommend → launch → monitor → adapt) within the hackathon demo timeframe.

### **5.4 Project Constraints**

* Time: 5-hour build window. Prioritise MVP: product recommendation UI \+ mock campaign launch \+ self-evolve demo.

* Resources: Team of 4, using one back-end/flex dev, two front-end devs, and one AI dev.

* Technology stack choices must align with available time and team experience.

---

## **6\. Appendices**

### **6.1 Use Case Diagram / Flow**

* Use Case 1: Seller logs in → views product recs → accepts product → campaign launched → monitors performance.

* Use Case 2: Agent automatically fetches data → scores products → presents to seller.

* Use Case 3: Agent monitors performance → updates scoring logic (self-evolve).

