# Secure Banking System – COE817 Project

## Overview

This project builds a secure banking system with a server and multiple ATM clients. Users can register, log in, and perform transactions like deposits, withdrawals, and balance checks. All communication is secured using encryption and authentication protocols.

## Features to Implement

### ✅ Core Components

-   **Bank Server**

    -   Listens for ATM client connections
    -   Spawns a new thread for each client request

-   **User Account System**

    -   Register with username and password
    -   Log in from ATM client

-   **Authenticated Key Distribution Protocol**

    -   Use a pre-shared key between ATM and server
    -   Must:
        -   Authenticate the customer to the server
        -   Authenticate the server to the ATM
        -   Generate a shared session key (Master Secret)

-   **Key Derivation**

    -   Derive two keys from the Master Secret:
        -   Encryption key
        -   MAC key (for data integrity)

-   **Secure Transactions**

    -   Support deposits, withdrawals, and balance checks
    -   Encrypt all data sent between ATM and server
    -   Use MACs to detect tampering
    -   Record each transaction in an encrypted audit log:
        -   Format: `CustomerID | Action | Timestamp`

-   **GUI Interfaces**
    -   Simple GUI for both ATM clients and bank server

---

## Demo Requirements

-   Log in as a customer and perform 2–3 actions
-   Verify the results in the audit log
-   Repeat with another customer
-   Be ready to explain your protocols to the TA

---

## Report Guidelines

-   **Length**: 10–20 pages
-   **Font**: Times New Roman, size 12

### Report Sections

1. **Introduction**

    - Goals and scope
    - Background info

2. **Design**

    - Implementation overview
    - Architecture diagram and module descriptions
    - Details of:
        - Key distribution protocol
        - Key derivation
        - Security for transactions

3. **Results**

    - Screenshots of GUI and outputs

4. **Conclusion**
    - What you learned
    - Member contributions
    - Leadership experience

> 📌 Include the names and student IDs of all group members

---

## Submission

-   Upload both your **report** and **source code** to the D2L submission folder
-   **Deadline: April 12, 2025**

---

## Group Info

-   Max group size: 4 students

## Academic Honesty

-   No copying or using online code
-   Any plagiarism results in a **zero** and will be reported

## 🚀 How to Run

### ✅ 1. Start the Bank Server

Open a terminal in the root project folder and run:

cd server
python server.py

### ✅ 2. Start the ATM Client

Open another terminal and run the following command:

cd client
python atm_client.py

Then you can register a new account and login with the same credentials
