# Daily network operation

This code is based on Norni framework, it helps you pull data from your network devices (Cisco). 


## HOW-TO set up

Kubernetes version : v1.16.x<br />
Sonarqube version : v8.2-community<br />
Artifactory version : v7.7.3 OSS<br />
Cert-manager version : v0.16.1<br />
Nginx version : v0.29.0<br />

### Step 1 - Deploy the NGINX Ingress Controller

Create a static ip

```
az network public-ip create --resource-group MC_Almond_support_francecentral --name supportStaticIP --sku Standard --allocation-method static --query publicIp.ipAddress -o tsv
```
