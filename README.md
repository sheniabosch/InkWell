# 🖋️ InkWell: Tattoo Health Classifier

![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![MobileNetV2](https://img.shields.io/badge/Model-MobileNetV2-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**InkWell** is an AI-powered detection system designed to distinguish between healthy healing and potential tattoo infections. By utilizing deep learning, this project aims to provide a reliable tool for tattoo artists and clients to monitor the healing process.

---

## 🧐 What It Does

InkWell uses a deep learning model to analyze tattoo photographs and answer the critical question:
> **"Is this tattoo healing normally, or is it showing signs of infection?"**

It helps identify early warning signs like excessive redness, swelling, and irritation, providing an accessible first-check for anyone concerned about their new ink.

---

## 📊 Final Results
*Evaluated on unseen test images*

| Metric | Value | Meaning (In Simple Words) |
| :--- | :--- | :--- |
| **Accuracy** | **93.8%** | Gets ~94 out of 100 tattoos right overall. |
| **Precision** | **97.1%** | When it flags "Infected," it’s correct 97% of the time. |
| **Recall** | **73.3%** | Catches 73% of real infections (prioritizing safety). |
| **Loss** | **0.55** | Low "confusion" on new photos (lower is better). |

### 📈 Visual Summary
Our AI is optimized to avoid false alarms—meaning it rarely scares users unnecessarily (only a 3% mistake rate on healthy tattoos)—while maintaining a solid 73% detection rate for real complications.

---

## 🛠️ How It Works

### 1. The Dataset
The model was trained using a combination of custom tattoo photos and large-scale public datasets containing both healthy skin and various skin infections.

### 2. The Architecture
We used **MobileNetV2**, a model pre-trained on millions of images, and fine-tuned it specifically for dermatological classification.

### 3. Training Strategies
* **Heavy Augmentation:** Randomized rotation, zoom, and brightness shifts to ensure the model works in "real-world" lighting.
* **Class Weights:** We gave extra focus to infected samples to ensure the model doesn't overlook them.
* **Early Stopping:** Prevents the model from "memorizing" the data, ensuring it actually *learns* the features of an infection.

---

## 🚀 Try It Yourself

1.  **Open in Colab:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)
2.  **Upload Data:** Connect your Google Drive or upload your photos directly to the notebook.
3.  **Run:** Execute the training cells to see the results and test the model on your own images.

---

## 🗺️ Future Ideas
- [ ] Incorporate more diverse photos of infected tattoos.
- [ ] Build a dedicated mobile app for on-the-go checks.
- [ ] Improve **Recall to 85%+** through further hyperparameter tuning.
- [ ] Conduct testing across a wider spectrum of skin tones.

---

**Made with 💜 & 🩷**
