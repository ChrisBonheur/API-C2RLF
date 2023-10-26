import base64
import io
import os
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from PIL import Image
import json

class CustomPagination(PageNumberPagination):
    page_size = 20  # Nombre d'éléments par page
    page_size_query_param = 'page_size'  # Paramètre pour spécifier le nombre d'éléments par page
    max_page_size = 100  # Nombre maximal d'éléments par page


def crop_image(path_image, width, height):
    try:
        # Ouvrir l'image avec Pillow
        image = Image.open(path_image)
        
        # Obtenir les dimensions de l'image
        img_width, img_height = image.size

        # Calculer les coordonnées du recadrage pour centrer l'image
        left = (img_width - width) / 2
        top = (img_height - height) / 2
        right = (img_width + width) / 2
        bottom = (img_height + height) / 2
        
        # Recadrer l'image
        image_cadree = image.crop((left, top, right, bottom))
        
        # Sauvegarder l'image recadrée au même emplacement
        image_cadree.save(path_image)  
    except Exception as e:
        print(f"Erreur lors du recadrage de l'image : {e}")
    

def edit_height_by_width(path_file, width_min):
    """edit height of image by new width given"""
    img = Image.open(path_file)
    img = img.convert('RGB')
    
    if img.width > width_min:
        img_height = img.height
        #get width image are depressed and we depressed this value from 
        #initial image height
        percentage_remove_px = (100 * (img.width - width_min)) / img.width#percentage of removing px
        output_height = (percentage_remove_px * img_height) / 100#get px to remove in height
        output_height = img_height - output_height#remove height 
        output_height = int(output_height)#convert height to integer
        
        output_size = (width_min, output_height)
        img.thumbnail(output_size)
        
        #save output image
        img.save(path_file)

def decode_response_to_json(response):
    return json.loads(response.content.decode('utf-8'))