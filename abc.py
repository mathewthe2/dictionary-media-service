image = "<img src=\"Anime_-_YourName_1_1.04.48.835.jpg\">"
image_path = image.split('src="')[1].split('">')[0]
print(image_path)