from xclip_handler import XCLIPHandler
import time

def main():
    print(f"Program začal")

    start_time = time.time()

    video_path = "../data/input/uvoz2-men3.mp4"
    
    # Uzavretý set kategórií, ak je potrebný
    closed_set_categories = [
        "person walking in an area", 
        "person waiting in place", 
        "person crossing the street", 
        "person using a device", 
        "person carrying something", 
        "person talking to someone", 
        "person sitting on a bench", 
        "person holding something", 
        "person riding a vehicle", 
        "person interacting with an object", 
        "person using public transport", 
        "person waiting for transport", 
        "person drinking", 
        "person shopping", 
        "person looking at something", 
        "person eating", 
        "person wearing something", 
        "person walking with someone", 
        "person with a companion", 
        "person performing physical activity"
    ]


    # Inicializácia handlera
    handler = XCLIPHandler(closed_set_categories=closed_set_categories)
    
    # Analyzovanie videa
    results = handler.analyze_video(video_path, batch_size=32)
    
    # Výstupy výsledkov
    for idx, result in enumerate(results):
        print(f"Dávka {idx+1}:")
        for i, prob in enumerate(result[0]):
            description = closed_set_categories[i]
            probability = prob.item() * 100  # Convert to percentage
            if probability > 5:
                print(f"Popis: {description} - Pravdepodobnosť: {probability:.2f}%")
        print("------------")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Program ukončený. Trvalo to {elapsed_time:.2f} sekúnd.")

if __name__ == "__main__":
    main()
