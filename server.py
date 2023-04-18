import socket
import azure.cognitiveservices.speech as speechsdk

HOST = "0.0.0.0"
PORT = 1234
speech_key, service_region = "65632c581ca44227a9bff65ffa389cae", "eastus"
speech_config = speechsdk.SpeechConfig(
    subscription=speech_key, region=service_region)

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

print("Say something...")


def speech_recognize_continuous_async_from_microphone(conn):
    """performs continuous speech recognition asynchronously with input from microphone"""
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)
    # The default language is "en-us".
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    done = False

    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        evt = evt.result.text
        msg = bytes(evt, 'UTF-8')
        print(evt)
        print(conn.send(msg))

    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        evt = evt.result.text
        msg = bytes(evt, 'UTF-8')
        print(evt)
        print(conn.send(msg))

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Perform recognition. `start_continuous_recognition_async asynchronously initiates continuous recognition operation,
    # Other tasks can be performed on this thread while recognition starts...
    # wait on result_future.get() to know when initialization is done.
    # Call stop_continuous_recognition_async() to stop recognition.
    result_future = speech_recognizer.start_continuous_recognition_async()

    # wait for voidfuture, so we know engine initialization is done.
    result_future.get()
    print('Continuous Recognition is now running, say something.')

    while not done:
        # No real sample parallel work to do on this thread, so just wait for user to type stop.
        # Can't exit function or speech_recognizer will go out of scope and be destroyed while running.
        print('type "stop" then enter when done')
        stop = input()
        print("runned")
        if (stop.lower() == "stop"):
            print('Stopping async recognition.')
            speech_recognizer.stop_continuous_recognition_async()
            break

    print("recognition stopped, main thread can exit now.")


with socket.socket() as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("server listenting at port ", PORT)
    conn, address = server_socket.accept()
    print("Connection from " + address[0] + ":" + str(address[1]))
    speech_recognize_continuous_async_from_microphone(conn)
