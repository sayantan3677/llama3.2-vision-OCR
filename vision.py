from flask import Flask, render_template, request, jsonify
import base64
import os
import ollama

app = Flask(__name__)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image upload and processing
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    # Save and encode the image
    image = request.files['image']
    image_path = os.path.join("uploads", image.filename)
    image.save(image_path)
    base64_image = encode_image(image_path)
    
    # Send image and prompt to the llama model
    try:
        response = ollama.chat(
            model='llama3.2-vision:90b',
            messages=[{
                "role": "user",
                "content":'list the name, date, and 1 alphanumeric nothing else. All 3 elements should be given comma separated',
                "images": [base64_image]
            }],
        )
        a = response.message.content
        parts = a.split(",")
        name = parts[0].strip()
        dob = parts[1].strip()
        adhaar_card_number = parts[2].strip()
        extracted_data = {"Name": name, "Date of Birth": dob, "Aadhar": adhaar_card_number}
        
        os.remove(image_path)
        print(extracted_data)
        return jsonify(extracted_data)
    except Exception as e:
        os.remove(image_path)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    # Run Flask app
    app.run(port=5000)
