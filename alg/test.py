import io,cv2,numpy as np
from pyjava.api.mlsql import RayContext

ray_context = RayContext.connect(globals(),"127.0.0.1:10001")

def resize_image(row):
    new_row = {}
    image_bin = row["content"]    
    oriimg = cv2.imdecode(np.frombuffer(io.BytesIO(image_bin).getbuffer(),np.uint8),1)
    newimage = cv2.resize(oriimg,(28,28))
    is_success, buffer = cv2.imencode(".png", newimage)
    io_buf = io.BytesIO(buffer)
    new_row["content"]=io_buf.getvalue()    
    return new_row

ray_context.foreach(resize_image)