## Add permissions to SageMaker Studio 

Before starting with the workshop, we need to add permissions to the IAM role used by SageMaker Studio, so that we can call Rekognition
from our notebook.

Go to the Amazon SageMaker console. Choose either the **Amazon SageMaker Studio** link on the left navigation pane, or
the **SageMaker Studio** button on the right side of the screen. 

<p align="center">
  <img src="images/sagemaker_1.png" alt="Mitotic figures" width="70%"/>
</p>

Select **sagemakeruser** from the list of Studio usernames. 

<p align="center">
  <img src="images/sagemaker_2.png" alt="Mitotic figures" width="70%"/>
</p>

Copy the Amazon Resource Name (ARN) of the role from the **User Details** panel, under **Execution role**. We will
only need the name of the role, which is the string after the forward slash.

In this case, it is _mod-6297809195fe4845-SageMakerExecutionRole-W7N5C7EVBIR0_. Your role will be named slightly
differently.

<p align="center">
  <img src="images/sagemaker_3.png" alt="Mitotic figures" width="70%"/>
</p>

Now go to the IAM console. From the left navigation pane, choose **Roles**.

<p align="center">
  <img src="images/iam_1.png" alt="Mitotic figures" width="70%"/>
</p>

In the search box, enter the first few letters of the role name you copied from the SageMaker console. Find the
role in the list following the search box, and select the role.

<p align="center">
  <img src="images/iam_2.png" alt="Mitotic figures" width="70%"/>
</p>

Choose the **Attach policies** button to attach a new policy to the role.

<p align="center">
  <img src="images/iam_3.png" alt="Mitotic figures" width="70%"/>
</p>

In the search box, enter _Rekognition_ and select the _AmazonRekognitionFullAccess_ policy by checking the box
next to it. Then, select **Attach policy**.

<p align="center">
  <img src="images/iam_4.png" alt="Mitotic figures" width="70%"/>
</p>

After completing these steps, return to the Amazon SageMaker console.
