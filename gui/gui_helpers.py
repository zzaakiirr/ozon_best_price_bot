def update_frames(index, frames, label, root):
    frame = frames[index]

    index += 1
    if index == len(frames):
        index = 0

    label.configure(image=frame)
    root.after(100, update_frames, index, frames, label, root)
