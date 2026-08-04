#!/usr/bin/env python
"""Generate TTS audio for video narration using Windows SAPI."""
import pyttsx3

def generate_narration():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed
    engine.setProperty('volume', 0.9)  # Volume
    
    # Read script
    with open("assets/video-narration-script.txt", "r", encoding="utf-8") as f:
        script = f.read()
    
    # Split by scene markers
    scenes = script.split("---SCENE")
    
    for i, scene in enumerate(scenes, 0):
        if scene.strip():
            # Extract scene number
            parts = scene.split("---", 1)
            scene_num = parts[0].strip() if len(parts) > 1 else str(i)
            text = parts[1].strip() if len(parts) > 1 else scene
            
            print(f"Generating scene {scene_num}...")
            engine.save_to_file(text, f"assets/narration-scene-{scene_num}.mp3")
    
    engine.runAndWait()
    print("✅ Narration generated: assets/narration-scene-*.mp3")

if __name__ == "__main__":
    generate_narration()
