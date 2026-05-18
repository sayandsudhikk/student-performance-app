from config import llm_config


def generate_evaluation(student_data: dict, teacher_comment: str) -> dict:
    """Call Vertex AI model with a prompt constructed from student data and comment.

    Two modes are supported:
    - If `llm_config.API_KEY` is set, perform a REST HTTP call using the key.
    - Otherwise, use the google-cloud-aiplatform client (requires ADC).

    Returns a dict with keys: pass_fail, confidence, explanation, recommendations
    """
    prompt = build_prompt(student_data, teacher_comment)
    # debug logging
    print("[LLM_SERVICE] prompt:\n", prompt)

    if llm_config.API_KEY and llm_config.USE_GEN_API:
        # Generative Language API path – uses a completely different JSON schema
        if not llm_config.GEN_MODEL:
            return {'error': 'GEN_MODEL is not set in llm_config.'}
        import requests as _requests
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{llm_config.GEN_MODEL}:generateContent"
        )
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": llm_config.API_KEY,
        }
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        try:
            resp = _requests.post(url, json=body, headers=headers, timeout=30)
            if not resp.ok:
                # Extract a human-friendly error message from the API response
                try:
                    err_body = resp.json()
                    api_msg = err_body.get('error', {}).get('message', resp.text)
                except Exception:
                    api_msg = resp.text
                print(f"[LLM_SERVICE] API error {resp.status_code}: {api_msg}")
                return {'error': f'Gemini API error ({resp.status_code}): {api_msg}'}
            jsonresp = resp.json()
        except _requests.exceptions.RequestException as e:
            print(f"[LLM_SERVICE] network error: {e}")
            return {'error': f'Network error calling Gemini API: {e}'}

        print("[LLM_SERVICE] generative API raw response:", jsonresp)
        # the generative language API returns candidates list
        output_text = ''
        if 'candidates' in jsonresp and jsonresp['candidates']:
            cand = jsonresp['candidates'][0]
            content = cand.get('content', {})
            # Gemini API: content = {role: ..., parts: [{text: "..."}]}
            if isinstance(content, dict):
                parts = content.get('parts', [])
                if parts and isinstance(parts[0], dict):
                    output_text = parts[0].get('text', '')
                elif 'text' in content:
                    output_text = content['text']
            elif isinstance(content, str):
                output_text = content
        # if output_text ended up empty, return raw response for debugging
        if not output_text:
            print("[LLM_SERVICE] empty text in generative API response:", jsonresp)
            return {'error': 'Gemini API returned an empty response. Check API key and model name.',
                    'raw_response': jsonresp}
        parsed = parse_llm_output(output_text)
        parsed['raw_response'] = jsonresp
        return parsed
    elif llm_config.API_KEY:
        # REST call using API key to Vertex endpoint
        if '<your-gcp-project-id>' in llm_config.PROJECT_ID or '<your-model-id>' in llm_config.MODEL_ID:
            raise ValueError("Please set PROJECT_ID and MODEL_ID in backend/config/llm_config.py before using the API key.")
        import requests
        url = (
            f"https://{llm_config.LOCATION}-aiplatform.googleapis.com/v1/"
            f"projects/{llm_config.PROJECT_ID}/locations/{llm_config.LOCATION}"
            f"/models/{llm_config.MODEL_ID}:predict"
        )
        headers = {"Authorization": f"Bearer {llm_config.API_KEY}"}
        body = {
            "instances": [{"content": prompt}],
            "parameters": {"temperature": 0.2}
        }
        resp = requests.post(url, json=body, headers=headers)
        resp.raise_for_status()
        output_text = resp.json().get('predictions', [{}])[0].get('content', '')
        return parse_llm_output(output_text)
    else:
        # default client path
        from google.cloud import aiplatform
        aiplatform.init(project=llm_config.PROJECT_ID, location=llm_config.LOCATION)
        model = aiplatform.gapic.PredictionServiceClient()
        name = llm_config.MODEL_NAME.format(
            project=llm_config.PROJECT_ID,
            location=llm_config.LOCATION,
            model_id=llm_config.MODEL_ID
        )
        request = {
            "instances": [{"content": prompt}],
            "parameters": {"temperature": 0.2}
        }
        response = model.predict(name=name, **request)
        output_text = response.predictions[0].get('content', '')
        return parse_llm_output(output_text)


def build_prompt(student_data: dict, teacher_comment: str) -> str:
    """Construct the LLM prompt following guidelines."""
    lines = []
    lines.append("You are given academic data for a student by subject. Determine pass or fail.")
    lines.append("Do NOT mention AI or algorithms. Provide exactly 3 improvement recommendations.")
    lines.append("Student data:")
    for rec in student_data.get('records', []):
        lines.append(f"Subject: {rec['subject']}, Score: {rec['subject_score']}, Attendance: {rec['attendance']}, Study hours: {rec['study_hours']}")
    lines.append(f"Teacher comment: {teacher_comment}")
    lines.append("Answer format:\nPassFail: <PASS/FAIL>\nConfidence: <0-100>%\nExplanation: <brief>\nRecommendations:\n1. ...\n2. ...\n3. ...")
    return "\n".join(lines)


def parse_llm_output(text: str) -> dict:
    """Extract structured data from the LLM output text."""
    result = {
        'pass_fail': None,
        'confidence': None,
        'explanation': None,
        'recommendations': []
    }
    for line in text.splitlines():
        if line.startswith('PassFail:'):
            result['pass_fail'] = line.split(':',1)[1].strip()
        elif line.startswith('Confidence:'):
            result['confidence'] = line.split(':',1)[1].strip()
        elif line.startswith('Explanation:'):
            result['explanation'] = line.split(':',1)[1].strip()
        elif line.strip().startswith(('1.','2.','3.')):
            result['recommendations'].append(line.strip()[3:].strip())
    return result
