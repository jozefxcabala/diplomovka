from xclip_handler import XCLIPHandler
import time

def main():
    print(f"Program začal")

    start_time = time.time()

    video_path = "../data/input/uvoz2-men.mp4"
    
    # Uzavretý set kategórií, ak je potrebný
    closed_set_categories = [
      "man waiting in place", 
      "person holding a box", # TODO je dolezite, mat konkretny vysek videa!!!!
      "person riding a bike", 
      "woman carrying a shopping bag", 
      "man walking on the street", 
    ]

    # Inicializácia handlera
    handler = XCLIPHandler(closed_set_categories=closed_set_categories)
    
    # Analyzovanie videa
    results = handler.analyze_video(video_path, batch_size=32)
    
    # Výstupy výsledkov
    for idx, result in enumerate(results):
        print(f"Dávka {idx+1}:")
        print(result)
        print("------------")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Program ukončený. Trvalo to {elapsed_time:.2f} sekúnd.")

if __name__ == "__main__":
    main()