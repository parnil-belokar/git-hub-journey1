import os
import json
import logging
from google.cloud import vision

# --------------------------------------------------
# SET GOOGLE CREDENTIALS (DO NOT COMMIT THIS FILE)
# --------------------------------------------------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(__file__), "instant-sound-456709-j3-9eba69829a2b.json"
)

# --------------------------------------------------
# LOGGING SETUP
# --------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class UrbanIssueAnalyzer:
    """
    AI Image Analysis Engine using Google Cloud Vision.
    Adds a governance-aware sanitation context layer.
    """

    SUPPORTED_ISSUES = [
        "pothole",
        "garbage",
        "water_leakage",
        "broken_pole",
        "overflow_drain",
        "streetlight_failure",
        "sanitation",
        "unknown",
    ]

    # --------------------------------------------------
    # LABEL → ISSUE MAPPING
    # --------------------------------------------------
    LABEL_MAPPING = {
        "pothole": ["pothole", "asphalt", "road", "crack", "rut", "damage", "tarmac"],
        "garbage": ["garbage", "waste", "trash", "litter", "dump", "debris", "plastic waste", "refuse"],
        "water_leakage": ["leak", "leakage", "pipe", "puddle", "water spill", "burst pipe", "plumbing"],
        "broken_pole": ["electric pole", "utility pole", "power line", "wire", "cable", "transformer"],
        "overflow_drain": ["drain", "sewer", "manhole", "overflow", "flooding", "gutter", "culvert"],
        "streetlight_failure": [
            "street light", "lamp post", "lighting", "fixture", "luminaire", 
            "electricity", "darkness", "lamp", "lantern", "outdoor lighting",
            "pole", "street lighting"
        ],
    }

    # --------------------------------------------------
    # SANITATION CONTEXT KEYWORDS
    # --------------------------------------------------
    SANITATION_CONTEXT = [
        "toilet",
        "urinal",
        "washroom",
        "bathroom",
        "restroom",
        "latrine",
        "sanitary",
    ]

    # --------------------------------------------------
    # SEVERITY CONFIG
    # --------------------------------------------------
    SEVERITY_CONFIG = {
        "pothole": (3, 8, 10),
        "garbage": (2, 8, 12),
        "water_leakage": (4, 8, 8),
        "broken_pole": (8, 10, 5),
        "overflow_drain": (8, 10, 5),
        "streetlight_failure": (5, 8, 6),
        "sanitation": (6, 9, 6),  # 🚨 public hygiene risk
        "unknown": (1, 3, 2),
    }

    def __init__(self):
        try:
            self.client = vision.ImageAnnotatorClient()
        except Exception as e:
            logging.warning(f"Vision client init failed: {e}")
            self.client = None

    # --------------------------------------------------
    # CONTEXT DETECTION
    # --------------------------------------------------
    def _detect_sanitation_context(self, labels):
        for label in labels:
            desc = label.description.lower()
            if any(keyword in desc for keyword in self.SANITATION_CONTEXT):
                return True
        return False

    # --------------------------------------------------
    # ISSUE MAPPING
    # --------------------------------------------------
    def _map_to_supported_issue(self, labels):
        scores = {issue: 0.0 for issue in self.SUPPORTED_ISSUES}
        # Boost keywords that indicate a problem
        PROBLEMATIC_KEYWORDS = ["broken", "damaged", "failure", "burst", "overflow", "crack", "leak", "dirty", "fallen"]

        for label in labels:
            desc = label.description.lower()
            conf = label.score

            for issue_type, keywords in self.LABEL_MAPPING.items():
                if any(keyword in desc for keyword in keywords):
                    # Base score is confidence
                    current_score = conf
                    
                    # Boost if the label itself mentions damage/problem
                    if any(prob in desc for prob in PROBLEMATIC_KEYWORDS):
                        current_score *= 1.2
                        
                    scores[issue_type] = max(scores[issue_type], current_score)

        # Special casing for streetlights (often labeled as 'night', 'darkness' etc.)
        night_score = 0
        for label in labels:
            desc = label.description.lower()
            if any(k in desc for k in ["night", "midnight", "darkness", "evening"]):
                night_score = max(night_score, label.score * 0.7) # Lower weight for darkness
        
        scores["streetlight_failure"] = max(scores["streetlight_failure"], night_score)

        best_issue, best_score = max(scores.items(), key=lambda x: x[1])

        if best_score == 0.0:
            return "unknown", 0.0

        return best_issue, min(best_score, 1.0) # Cap at 1.0

    # --------------------------------------------------
    # SEVERITY CALCULATION
    # --------------------------------------------------
    def _calculate_severity(self, issue_type, objects):
        base, max_sev, scale = self.SEVERITY_CONFIG.get(issue_type, (1, 3, 2))
        max_area = 0.0

        for obj in objects:
            vertices = obj.bounding_poly.normalized_vertices
            if len(vertices) == 4:
                # Area of normalized bounding box
                width = max(v.x for v in vertices) - min(v.x for v in vertices)
                height = max(v.y for v in vertices) - min(v.y for v in vertices)
                max_area = max(max_area, width * height)

        if max_area == 0.0:
            max_area = 0.1

        severity = base + (max_area * scale)
        return min(round(severity), max_sev)

    # --------------------------------------------------
    # MAIN ANALYSIS FUNCTION
    # --------------------------------------------------
    def analyze_image(self, image_path: str) -> str:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_path, "rb") as f:
            content = f.read()

        if not self.client:
            return json.dumps({"error": "Vision client not initialized"})

        image = vision.Image(content=content)

        try:
            label_response = self.client.label_detection(image=image)
            object_response = self.client.object_localization(image=image)
        except Exception as e:
            logging.error(f"Vision API error: {e}")
            return json.dumps({"error": f"API Error: {str(e)}"})

        labels = label_response.label_annotations
        objects = object_response.localized_object_annotations

        # 🔹 STEP 1: CONTEXT CHECK
        sanitation_context = self._detect_sanitation_context(labels)

        # 🔹 STEP 2: NORMAL MAPPING
        issue_type, confidence = self._map_to_supported_issue(labels)
        confidence_percent = int(confidence * 100)

        # 🔹 STEP 3: GOVERNANCE OVERRIDE
        if sanitation_context:
            logging.info("Sanitation context detected - applying override")
            issue_type = "sanitation"
            confidence_percent = max(confidence_percent, 80)

        logging.info(f"AI Detection: mapped to '{issue_type}' with {confidence_percent}% confidence")
        if labels: 
             top_labels = ", ".join([f"{l.description}({l.score:.2f})" for l in labels[:5]])
             logging.info(f"Top Labels: {top_labels}")

        # Lowered threshold to 40% as urban issues are often generic in Vision AI
        if confidence_percent < 40:
            logging.info(f"Confidence {confidence_percent}% below threshold (40%) - reverting to unknown")
            issue_type = "unknown"

        # 🔹 STEP 4: SEVERITY
        severity_score = self._calculate_severity(issue_type, objects)

        result = {
            "issue_type": issue_type,
            "confidence_percent": confidence_percent,
            "severity_score": severity_score,
        }
        logging.info(f"Final AI Result: {result}")

        return json.dumps(result, indent=2)


# --------------------------------------------------
# CLI TEST
# --------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UrbanSathi Image Analyzer")
    parser.add_argument("--image", type=str, required=True)
    args = parser.parse_args()

    analyzer = UrbanIssueAnalyzer()
    print(analyzer.analyze_image(args.image))