from flask import Flask, request, jsonify, render_template
import plotly.express as px

app = Flask(__name__)

# -------------------------------
# VALIDATION
# -------------------------------
def is_valid_dna(seq):
    valid = set("ATGC")
    return set(seq.upper()).issubset(valid)

# -------------------------------
# VARIANT DETECTION
# -------------------------------
def detect_variants(ref, sample):
    variants = []

    min_len = min(len(ref), len(sample))

    # SNP detection
    for i in range(min_len):
        if ref[i] != sample[i]:
            variants.append({
                "position": i + 1,
                "ref": ref[i],
                "alt": sample[i],
                "type": "SNP"
            })

    # Handle insertions
    if len(sample) > len(ref):
        for i in range(len(ref), len(sample)):
            variants.append({
                "position": i + 1,
                "ref": "-",
                "alt": sample[i],
                "type": "INS"
            })

    # Handle deletions
    elif len(ref) > len(sample):
        for i in range(len(sample), len(ref)):
            variants.append({
                "position": i + 1,
                "ref": ref[i],
                "alt": "-",
                "type": "DEL"
            })

    return variants

# -------------------------------
# PLOT
# -------------------------------
def create_plot(variants):
    if not variants:
        return None

    positions = [v["position"] for v in variants]

    fig = px.scatter(
        x=positions,
        y=[1] * len(positions),
        title="Mutation Positions",
        labels={"x": "Position", "y": ""}
    )

    return fig.to_html(full_html=False)

# -------------------------------
# ROUTES
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json

    ref = data.get("reference", "").upper().strip()
    sample = data.get("sample", "").upper().strip()

    # Validation
    if not ref or not sample:
        return jsonify({"error": "Both sequences required"}), 400

    if not is_valid_dna(ref) or not is_valid_dna(sample):
        return jsonify({"error": "Invalid DNA sequence (only A, T, G, C allowed)"}), 400

    variants = detect_variants(ref, sample)
    plot = create_plot(variants)

    return jsonify({
        "variants": variants,
        "count": len(variants),
        "plot": plot
    })


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    content = file.read().decode('utf-8')

    return jsonify({"sequence": content.strip()})


@app.route('/ai', methods=['POST'])
def ai():
    data = request.json
    count = data.get("count", 0)

    # Simple heuristic "AI"
    if count > 10:
        result = "⚠️ High mutation load — possible biological significance"
    elif count > 3:
        result = "🟡 Moderate mutations — review recommended"
    else:
        result = "✅ Low mutation count — likely normal variation"

    return jsonify({"result": result})


# -------------------------------
# RUN
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True,port=8000, use_reloader=False)