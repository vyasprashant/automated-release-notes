# Release Notes - Test-release-0.1.0

Hello there,

We are glad to inform you that the latest version **Test-release-0.1.0** of **Go CI/CD** is out. Below are the Jira issues included in this release.

## **Summary**  
### **Bugs**
Fixed errors related to RHACS scanning images in ghcr.io and AWS, provisioning not running, GitLab runners not working on UOCP, service account issue in Argo Workflows, and entry point recognition issue in Quay tagged images. Added ability to defer or mark a CVE as false-positive for one namespace without affecting others. Resolved errors with the whalesay demo app.

### **Storys**
The update includes various tasks related to the S&T Business Data Scientists Gitlab project. This involves updating a Confluence article on deferring vulnerabilities with RHACS 4.5, enabling the Application Deployment team to check out all projects for an application into one folder for testing and updates. The SmartLab Product Team aims to deploy applications to the PRD environment and test the setup of the GitLab "Test" runner. Product Teams will now be able to view "demo" applications in ArgoCD, with the creation of an ArgoCD instance on the Sandbox cluster. The focus is on working with namespaces instead of projects, running regular RIS hypercare follow-ups with Openshift and Grecis operations teams, and addressing post-mortem INC1725025. Other tasks include provisioning SSU Smart Submission, knowledge transfer with Damien, and upgrading the ArgoCD image updater.

### **Tasks**
Product Team tasks include automating incident assignments, updating HOPEX source code repository, documenting application logs references, removing unused namespaces, ensuring CMDB fields are correctly filled, updating firewall rules, changing access control for PostgreSQL DB server, connecting SonarQube to EntraID, deploying applications in DEV: ART, updating CMDB fields for Apigee and Kafka, moving demo applications to SOCP Sandbox Openshift, on-boarding the "Frames" team, pushing code to Gitlab, deploying in production, integrating dashboarding tool for SmartLab metrics, updating checklist for application transitions, fixing vulnerabilities in argocd-image-updater, providing procedures for out-of-hours RIS outages, planning Openshift post-mortems, enabling Risk-related notifications, and provisioning access management for RHACS and Quay. Additionally, updating Quay provisioning scripts and argocd-image-updater are planned.

## **Detailed Issues List**

| Priority  | Key   | Summary | Status  |
|-----------|------|---------|---------|
| Major | CICD-385 | RHACS error message cannot scan images in ghcr.io and aws | To Do |
| Major | CICD-372 | Fix issue with the Provisioning not running | Done |
| Major | CICD-361 | Fix the issue with the GitLab runners not working on UOCP | Done |
| Major | CICD-357 | Fix service account issue in Argo Workflows | Done |
| Major | CICD-351 | RHACS : for a CVE be able to defer or mark as false-positive for one namespace without affecting all namespaces it appears in | On-Hold |
| Major | CICD-346 | Fix the whalesay demo app that is in error | Backlog |
| Major | CICD-335 | Issue where the entry point to tagged images in Quay is not recognised  | Backlog |
| Major | CICD-384 | S&T Business Data Scientists Gitlab project | To Do |
| Major | CICD-383 | Update Confluence article on how to defer vulnerability with RHACS 4.5 | Done |
| Major | CICD-381 | As a member of the Application Deployment team I wish to be able to check out all the projects for an application into one folder so I can merge in a new release, test the build locally and then quickly check in the updates | Done |
| Major | CICD-374 | As SmartLab Product Team I need to be able to deploy the application to the PRD environment | Done |
| Minor | CICD-370 | Test the setup of the GitLab "Test" runner (different to the builder runners) | Backlog |
| Major | CICD-345 | Product Teams need to be able to see the "demo" applications in ArgoCD | Done |
| Major | CICD-337 | Create an ArgoCD instance on the Sandbox (SOCP) cluster | Done |
| Critical | CICD-336 | Work with namespaces instead of projects | Done |
| Major | CICD-334 | Set up and run regular RIS hypercare follow-up with Openshift and Grecis operations teams | Done |
| Major | CICD-333 | Post-mortem INC1725025 | Done |
| Minor | CICD-332 | Provision SSU Smart Submission | Done |
| Major | CICD-326 | KT with Damien | Done |
| Major | CICD-324 | Upgrade ArgoCD image updater | Done |
| Major | CICD-382 | As a member of a Product Team I need incidents to be assigned to my team automatically | In Progress |
| Major | CICD-380 | Update or remove HOPEX source code repository | Backlog |
| Major | CICD-379 | Document and publish reference for Product Teams for application logs | Backlog |
| Major | CICD-378 | Remove namespace devops-uocp (if not used anymore) | To Do |
| Major | CICD-376 | Remove non-compliant namespaces UOCP Openshift cluster | On-Hold |
| Major | CICD-375 | Ensure that in CMDB these fields for an application are filled and with correct data: Resolver Team, Application Support and Application Folder URL | Done |
| Major | CICD-373 | Ticket to EB-Qual to update Partner Portal firewall for the pgroup PSA_JEE to allow access to mgmt.socp.givaudan.com | In Progress |
| Major | CICD-371 | Follow-up & validate the change for the PostgreSQL DB server access control to utilize subnet masks instead of individual server listings | Done |
| Major | CICD-369 | Connect Test SonarQube to EntraID | Done |
| Major | CICD-368 | Accompany Product Team to first deployment in DEV: ART | Done |
| Major | CICD-367 | Update CMDB application fields for Apigee | On-Hold |
| Major | CICD-366 | Move demo applications to SOCP Sandbox Openshift | Backlog |
| Major | CICD-365 | Update the demo app "versioned demon" to create multiple tags on the image in quay  | Backlog |
| Major | CICD-360 | On-board the "Frames" product team | Done |
| Major | CICD-359 | Push the "Frames" code to Gitlab | Done |
| Major | CICD-358 | Support the "Frames" team to deploy in production | Done |
| Major | CICD-356 | Integrate dashboarding tool for SmartLab metrics | Backlog |
| Major | CICD-355 | Update CMDB application fields for Kafka | On-Hold |
| Major | CICD-354 | Update Checklist for Application Transition to PRD into separate articles replacing how-to | Done |
| Major | CICD-352 | Fix Critical Vulnerabilities in argocd-image-updater v0.12.0 on OCP | Done |
| Major | CICD-350 | S&T Grecis Product Team provide procedure in case of out-of-hours RIS outage eg after an upgrade | Done |
| Major | CICD-349 | UOCP z stream upgrade online in July | Done |
| Major | CICD-348 | Follow AIOps monitoring evolution | Backlog |
| Major | CICD-347 | Decide to silence GivaudanPodNotHealthy on UOCP or take actions to handle incidents | On-Hold |
| Major | CICD-344 | Post-mortem for Openshift planned changes that cause application outages | Done |
| Major | CICD-342 | Enable the Risk-related notifications for the containers scanned by RHACS | Backlog |
| Major | CICD-331 | Provision access management for RHACS | Backlog |
| Major | CICD-330 | Provision access management for Quay | Backlog |
| Major | CICD-325 |  Update argocd-image-updater to V0.12.0 | Done |
| Major | CICD-323 | Refactor Quay provisioning script | Backlog |

A big shoutout to these amazing individuals who helped make this release a success! 🎉
Thanks,
**Go CI/CD**