
input_video = "License Plate Detection Test_1080p.mp4"
ffmpeg.input(input_video).output("frames/frame_%06d.jpg", vf=f"fps={5}").run()
