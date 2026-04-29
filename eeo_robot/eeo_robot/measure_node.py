import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image  
from cv_bridge import CvBridge     
import os
import cv2
import numpy as np
from ament_index_python.packages import get_package_share_directory
from rclpy.qos import QoSProfile, DurabilityPolicy

class EeoMeasureNode(Node):
    def __init__(self):
        super().__init__('eeo_measure_node')  
        
        qos_profile = QoSProfile(            
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        

        self.publisher_ = self.create_publisher(String, '/robot_description', qos_profile)

        self.image_publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        
        self.bridge = CvBridge()
        self.timer = self.create_timer(1.0, self.publish_robot)
        
        self.current_pixels = 500.0
        

        try:
            share_dir = get_package_share_directory('eeo_robot')
            self.urdf_path = os.path.join(share_dir, 'urdf', 'eeo_robot.urdf')
        except Exception:
            self.urdf_path = os.path.expanduser('~/ros2_ws/src/eeo_robot/urdf/eeo_robot.urdf')

    def get_electrode_data(self):
        # 1. Уменьшаем длину на 2 пикселя за каждый шаг (симуляция износа)
        self.current_pixels -= 2.0
    
        # 2. Цикл: если электрод "сточился" до 300 пикселей, ставим новый (500)
        if self.current_pixels < 300:
            self.get_logger().warn('Электрод изношен! Замена на новый...')
            self.current_pixels = 500.0

        pixels_to_show = int(self.current_pixels)

        # Далее отрисовка как была
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(frame, (300, 50), (340, 100), (128, 128, 128), -1)
        cv2.line(frame, (320, 100), (320, 100 + pixels_to_show), (255, 255, 255), 3)
        cv2.putText(frame, f"Length: {pixels_to_show}px", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        mm_per_pixel = 0.6
        length_m = (pixels_to_show * mm_per_pixel) / 1000.0
    
        return length_m, frame


    def publish_robot(self):
        if not os.path.exists(self.urdf_path):
            self.get_logger().error(f'Файл URDF не найден: {self.urdf_path}')
            return

        # олучаем данные и "картинку"
        length, frame = self.get_electrode_data()

        # Публикуем изображение в ROS
        img_msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
        self.image_publisher.publish(img_msg)

        # Читаем и обновляем URDF
        with open(self.urdf_path, 'r') as f:
            content = f.read()
        
        updated_content = content.replace("{L_VALUE}", f"{length:.3f}")
        updated_content = updated_content.replace("{L_HALF}", f"{length/2:.3f}")
        
        # Публикуем модель робота
        msg = String()
        msg.data = updated_content
        self.publisher_.publish(msg)
        
        self.get_logger().info(f'Обновлено. Электрод: {length:.3f}м ({int(length*1000/0.6)}px)')

def main(args=None):
    rclpy.init(args=args)
    node = EeoMeasureNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

