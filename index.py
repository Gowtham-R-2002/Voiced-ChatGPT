from flask import Flask, request, jsonify
import assemblyai as aai
import openai
import requests
from gtts import gTTS
from pydub import AudioSegment
import io
import speech_recognition as sr
import wave

app = Flask(__name__)

# Set your AssemblyAI and OpenAI API keys
openai_api_key = "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"

# Configure OpenAI API key
openai.api_key = openai_api_key

tts_base_url = "https://texttospeech.googleapis.com/v1/text:synthesize"

@app.route('/', methods=['GET'])
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Voice Recorder</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw==" crossorigin="anonymous" referrerpolicy="no-referrer" />
</head>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js" integrity="sha384-I7E8VVD/ismYTF4hNIPjVp/Zjvgyol6VFvRkX/vR+Vc4jQkC+hVqc2pM8ODewa9r" crossorigin="anonymous"></script>
</head>
<style>
body{
    background-color: #03191E;
    color: #C1CFDA;
    padding-top:5%;
}
textarea{
    background-color: #03191E !important;
    color: #C1CFDA !important;
}
    .container{
    text-align: center;
    margin-bottom:30%;
}
#recordButton{
    margin-top: 5rem;
    scale: 2;
    border-radius: 200% !important;
}
.fixed-bottom{
background-color:#07020D;
 color: #C1CFDA;
 padding: 2%;
border-radius: 5%;
}
</style>
<body>

    <div class="container">
        <div class="row">
            <h1>Voice enabled ChatGPT Development</h1>
        </div>
        <div class="div">
            <button id="recordButton" class="btn btn-outline-light btn-lg"><i id="ic" class="fa-solid fa-microphone"></i></button>
            <h4 id="content" style="margin-top:30px;">Click to record</h4>
        </div>
        <br>
        <br>
        <div class="row">
            <div class="col-lg-6 col-mg-6">
                <h4>Your Text:</h4>
                <textarea class="form-control cus-height" id="aud-con" rows="8" disabled></textarea>
            
            </div>
            <div class="col-lg-6 col-mg-6">
            <h4>Reply</h4>
                <textarea class="form-control cus-height" id="gpt-con" rows="8" disabled></textarea>
                
            </div>
            
        </div>
        <br>
        <button id="stopButton" class="btn btn-outline-light btn-lg">Stop</button>
        
        <div class="fixed-bottom">
            
            <h5>Created with passi<i class="fa fa-heart"> </i>n by Roman RG.</h5>
        </div>
        
        
    </div> 
    
    <script>
        $(document).ready(function () {
            const recordButton = $('#recordButton');
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;

            recordButton.on('click', async function () {
                $('#content').text("Recording...Click the buttton to stop.")
                if (!isRecording) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);

                        mediaRecorder.ondataavailable = function (event) {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = function () {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            sendAudioToServer(audioBlob);
                        };

                        mediaRecorder.start();
                        isRecording = true;
                        $('#ic').attr("class","fa-solid fa-microphone fa-bounce");
                    } catch (error) {
                        console.error('Error accessing the microphone:', error);
                    }
                } else {
                    mediaRecorder.stop();
                    isRecording = false;
                    $('#ic').attr("class","fa-solid fa-microphone");
                    $('#content').text("Audio Recorded...Wait till ChatGPT Responses.");
                }
            });

            async function sendAudioToServer(audioBlob) {
                const formData = new FormData();
                formData.append('audio', audioBlob);

                try {
                    const response = await $.ajax({
                        url: '/transcribe_audio',
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false
                    });

                    const transcribedText = response;
                    console.log(transcribedText);
                    $('#aud-con').val(transcribedText);
                    // Use the transcribedText as input to GPT-3 and implement TTS to get audio response
                    getGPT3Response(transcribedText);
                    audioChunks=[];
                } catch (error) {
                    console.error('Error during AJAX request:', error);
                }
            }

            async function getGPT3Response(promptText) {
                try {
                    const gpt3Response = await $.ajax({
                        url: '/get_gpt3_response',
                        type: 'POST',
                        data: JSON.stringify({ 'prompt_text': promptText }),
                        processData: false,
                        contentType: 'application/json'
                    });

                    // Use the gpt3Response to handle the GPT-3 response
                    console.log('GPT-3 Response:', gpt3Response);
                    myText=gpt3Response.gpt3_response;
                    console.log(myText);
                    const textToSpeak = myText.trim();
                    console.log(textToSpeak);
                   

            if (textToSpeak !== '') {
                speakText(textToSpeak);
            }
            function stopSpeech() {
                if ('speechSynthesis' in window && speechSynthesis.speaking) {
                speechSynthesis.cancel();
                }
            }


            const stopButton = document.getElementById('stopButton'); 

            stopButton.addEventListener('click', stopSpeech);


           function speakText(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US';

  // Get the list of available voices
  let voices = speechSynthesis.getVoices();

  // Find the female voice (you may need to adjust the index or the criteria to match the desired female voice)
  let femaleVoice = voices.find(voice => voice.name.includes('Zira'));

  // If a female voice is found, set it as the voice for the utterance
  if (femaleVoice) {
    utterance.voice = femaleVoice;
  } else {
    console.warn("Female voice not found. Using the default voice.");
  }

  // Display the text to be spoken in an HTML element with id "gpt-con"
  $('#gpt-con').val(text);

  // Display a message to indicate that the response is ready
  $('#content').text("Here is your response :)");

  // Speak the text using the selected voice
  speechSynthesis.speak(utterance);
}



                    

                        
                } catch (error) {
                    console.error('Error during GPT-3 request:', error);
                }
            }

            

           
            
        });


    </script>
</body>
</html>

    '''

@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():

    audio_file = request.files['audio']
    audio = AudioSegment.from_file(io.BytesIO(audio_file.read()))
    wav_audio = io.BytesIO()
    audio.export(wav_audio, format='wav')

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Use the recognizer to transcribe the audio
    with sr.AudioFile(wav_audio) as source:
        audio_data = recognizer.record(source)

    # Perform the speech recognition
    try:
        transcribed_text = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        transcribed_text = "Speech Recognition could not understand the audio."
    except sr.RequestError as e:
        transcribed_text = f"Error occurred while transcribing audio: {e}"

    return transcribed_text

    
@app.route('/get_gpt3_response', methods=['POST'])
def get_gpt3_response():
    data = request.get_json()
    prompt_text = data.get('prompt_text', '')

        # Call the GPT-3 API
    response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt_text,
            max_tokens=150
        )

    gpt3_response = response['choices'][0]['text']
    

    return jsonify(gpt3_response=gpt3_response)




if __name__ == '__main__':
    app.run()
