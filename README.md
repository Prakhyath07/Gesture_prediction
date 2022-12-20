# Gesture Prediction using Machine Learning

Natural control methods based on surface electromyography (sEMG) and pattern
recognition are promising for hand prosthetics. However, the control robustness offered
by scientific research is still not sufficient for many real life applications, and commercial
prostheses are capable of offering natural control for only a few movements. In recent
years deep learning revolutionized several fields of machine learning, including
computer vision and speech recognition.
The goal is to predict the gestures based on the data recorded by the MYO Thalmic
bracelet.



Data Set Information:

For recording patterns, we used a MYO Thalmic bracelet worn on a userâ€™s forearm, and a PC with a Bluetooth receiver. The bracelet is equipped with eight sensors equally spaced around the forearm that simultaneously acquire myographic signals. The signals are sent through a Bluetooth interface to a PC.
We present raw EMG data for 36 subjects while they performed series of static hand gestures.The subject performs two series, each of which consists of six (seven) basic gestures. Each gesture was performed for 3 seconds with a pause of 3 seconds between gestures.

Number of Instances is about 40000-50000 recordings in each column (30000 listed as guaranteed)

Source:https://archive.ics.uci.edu/ml/datasets/EMG+data+for+gestures


## Tech Stack Used

1. Python 
2. FastAPI 
3. Machine learning algorithms
4. Docker
5. MongoDB
6. GitHub Actions
7. Cassandra
8. GCP VM and artifact registry
9. AWS S3
