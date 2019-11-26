# Capstone
# Network Security using Primitive Memory
COMP 499 Senior Capstone Project

The goal of this capstone is to test the notion of primitive memory (a binary string of data, data being the "past events") being viable for a machine learning application. Successful primitive memory instance, after supervised learning is done, will be able to successfully, on average, raise flags when the network chatter suggests either an attack or other abnormal behaviors that should not happen.
The capstone is comprised of three main parts:
  1. Creating a server-client application simulating basic traffic light behavior on an intersection. This will be used as a basis      for the primitive memory to learn and try to protect (Application is created using Python 3).
  2. Creating a data structure, represeted as an inverted prefix tri, to house and power the primitive memory. Root will contain the complete memory (string of bits), while the children nodes will represent different prefixes comprising the full string (Application is created using Python 3).
  3. Using AWS SageMaker to train the memory and test it on the traffic light simulator from point (1).
