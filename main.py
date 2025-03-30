import base
import flower
import leaf
import stem

# Add your main logic here
if __name__ == "__main__":
    PAR = flower.gen_params()
    flower.draw_flower(PAR, filename="flower.png")
    # flower.draw_flower(PAR, azim=0, elev=90, filename="flower_top.png")   # Top-down
    # flower.draw_flower(PAR, azim=45, elev=45, filename="flower_iso.png")  # Isometric
    # flower.draw_flower(PAR, azim=90, elev=20, filename="flower_side.png") # Side-view
    center = {}
    base.draw_base("test.png", center)
    print(center)

