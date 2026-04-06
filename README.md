# InkWell: Tattoo Health Classifier
AI-powered detection of healthy vs. infected tattoos
  TensorFlow
  MobileNetV2
  Accuracy
  Recall
  Precision
What It Does
InkWell uses deep learning to look at tattoo photos and answer:
"Is this tattoo healthy or showing signs of infection?"
It helps tattoo artists, clients, and doctors spot early warning signs (redness, swelling, etc.) quickly and reliably.
Final Results (on unseen images)




Visual Summary (for non-technical friends)
  Project Overview
  
  Our AI is very good at avoiding false alarms (only 3% mistakes when it warns about infection) and catches 73% of real problems.
How It Works (in simple steps)
Data: Your own tattoo photos + big public datasets (healthy tattoos + skin infections)
Smart Model: Uses MobileNetV2 (pre-trained on millions of images) + custom training
Training Tricks:
Heavy image changes (rotation, zoom, brightness) to make it robust
Extra focus on infected tattoos (class weights)
Stops early if it starts memorizing instead of learning
Try It Yourself
Open the notebook in Google Colab: Open In Colab
Upload your own tattoo photos to Google Drive (or just use the downloaded ones)
Run the notebook — it downloads data, trains the model, and shows results!
Future Ideas
Add more real infected tattoo photos
Make a phone app for easy use
Improve recall to 85%+ with more fine-tuning
Test on different skin tones
Made with 💜 & 🩷
