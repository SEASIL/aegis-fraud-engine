# 🚀 Aegis Fraud Engine Hosting Guide

This guide explains how to host the **Aegis Fraud Engine** (Spring Boot API + MongoDB + Web Dashboard) on the cloud for free using Render and MongoDB Atlas.

## Step 1: Set up a Free Cloud Database (MongoDB Atlas)

Since you don't want to run MongoDB locally in production, we will use MongoDB Atlas.

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) and sign up.
2. Create a **New Cluster** and select the **M0 Free Tier** (available on AWS/GCP/Azure).
3. Under **Database Access**, create a new database user (e.g., username `fraud_user`, password `your_password`).
4. Under **Network Access**, click `Add IP Address` -> `Allow Access from Anywhere` (`0.0.0.0/0`) so Render can connect to it.
5. Click **Connect** -> **Drivers** -> **Java** and copy the **Connection String**.
   * It will look like this: `mongodb+srv://fraud_user:your_password@cluster0.mongodb.net/?retryWrites=true&w=majority`
   * **Note:** Change `.net/?` to `.net/fraud_inference?` so it saves logs to the `fraud_inference` database.

---

## Step 2: Deploy to Render (Free PaaS)

Render allows you to host web applications directly from GitHub for free.

1. Commit and push these recent changes to your GitHub repository:
   ```bash
   git add .
   git commit -m "Add Cloud configs and Web UI dashboard"
   git push origin main
   ```
2. Go to [Render](https://render.com/) and create a free account.
3. Click **New +** and select **Web Service**.
4. Connect your GitHub account and select the `aegis-fraud-engine` repository.
5. **Configuration:**
   - **Name:** `aegis-fraud-engine` (or whatever you prefer)
   - **Root Directory:** `fraud-backend`
   - **Environment:** `Docker`
   - **Instance Type:** `Free`
6. Scroll down to **Environment Variables** and click `Add Environment Variable`:
   - **Key:** `SPRING_DATA_MONGODB_URI`
   - **Value:** Paste the MongoDB Atlas connection string from Step 1.
7. Click **Create Web Service**. 
8. Render will now build your Docker container. This usually takes 3-5 minutes.

---

## Step 3: Test and Use the Web Dashboard!

Once Render shows the service as **Live**, click the public URL provided at the top left (e.g., `https://aegis-fraud-engine.onrender.com`).

- **Interactive Web UI:** The beautiful dashboard will automatically load! You can click the preset buttons and run live ONNX model inference instantly.
- **REST API:** Developers can hit `https://your-url.onrender.com/predict` via cURL, Postman, or external applications.
- **Resilience:** If your free MongoDB Atlas cluster takes a moment to wake up, the Spring Boot application will still return fraud predictions flawlessly without throwing 500 Server Errors!

---

### Alternative: Run Anywhere with Docker Compose

If you have a Linux VPS (AWS EC2, DigitalOcean) and want to self-host everything, just run:

```bash
docker-compose up -d --build
```
This automatically spins up:
1. `fraud_postgres` (PostgreSQL for data pipeline)
2. `fraud_mongodb` (MongoDB for inference logs)
3. `fraud_backend_api` (The Spring Boot API & Dashboard on port `8080`)
