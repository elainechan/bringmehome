# Bring Me Home: Crowdsourcing Pet Retrieval

Cat escaped from the door? Dog ran away off-leash? Push a button or cry out loud, and Bring Me Home will automatically alert neighbors that your pet is missing. When someone finds your pet, you will be notified to arrange a pick-up.

In cases of missing persons, the sooner a search begins, the higher the likelihood of finding the person. This is why <a href="https://a858-nycnotify.nyc.gov/notifynyc/">Notify NYC</a>, New York City's emergency alert service, utilizes crowdsourcing to locate missing persons. Notify NYC sends real-time texts to all subscribers, detailing the visual characteristics of recently missing persons, so that more eyes are enlisted on the lookout. Bring Me Home takes this concept and applies it to pets.

Bring Me Home combines Rekognition image recognition techniques, programmed wireless Internet of Things (IoT) buttons, and intelligent assistant Alexa to implement a solution that increases the chances of retrieving a lost pet.

# Credits

Image recognition: James Beswick, Rachel
Backend: Alex Srisuwan
Frontend: Elizabeth Funk
Devices: Elaine Chan

# Architecture:

* DynamoDB table, partition on `id`
* 6 Functions (1 per Python file)
* API Gateway fronts `Register` and `Found`
* S3 Bucket

# Follow-Ups:

* Alexa:
  * Report missing
  * Pet Found
  * Verify Found
  * Geolocation
  * Push notifications to subscribers when pet is reported missing
* Hardware:
  * Is my pet at home?

# Workflow:

 1. Register:

    1. Post:
    ```
    {
        "image": string (base 64 encoded image),
        "PetName": string,
        "OwnerPhone": string (no spaces/hyphens)
    }
    ```
    to register a pet in the system. The lambda function will put an entry in DynamoDB, then decode the image, and store it in S3.

    S3 bucket upload triggers `ProcessImageInRekognition` lambda, which sends the image to Rekognition, then gets breed information using `GetBreedFromRekognition` lambda, and puts breed information in the DynamoDB entry.

2. Report Missing: 
    Register IoT buttons with your ID in the `ReportLost` lambda.
    Pushing the IoT button updates DynamoDB entry to set `PetStatus` to `Lost`.

3. Report Found:

     1. Post:
     ```
     {
        "image": string (base64 encoded image)
     }
    ```
    to `Found` lambda. This is done by a subscriber of the system when he/she finds a pet that is reported missing in the system. The lambda function sends the image to Rekognition, gets the breed information using the `GetBreedFromRekognition` lambda, then queries DynamoDB for lost dogs of that breed, returning a list of phone numbers of possible owners.

4. Verify Found:
    1. Register IoT buttons with your ID in the `VerifyFound` lambda. When a pet is returned to its owner, an IoT button push updates the DynamoDB entry to set `PetStatus` to `Found`