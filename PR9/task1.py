import cv2

def apply_watermark(source_image, watermark_image, output_file, transparency=0.4):
    # Завантажуємо основне зображення та водяний знак
    main_image = cv2.imread(source_image)
    watermark = cv2.imread(watermark_image)

    # Перевіряємо, чи файли завантажилися успішно
    if main_image is None or watermark is None:
        print("Не вдалося завантажити зображення або водяний знак.")
        return

    # Визначаємо розміри зображення та водяного знака
    img_height, img_width, _ = main_image.shape
    wm_height, wm_width = watermark.shape[:2]

    # Перевірка на відповідність розмірів
    if wm_height > img_height or wm_width > img_width:
        print("Водяний знак занадто великий для зображення.")
        return

    # Розміщуємо водяний знак у правому нижньому куті
    x_start = img_width - wm_width
    y_start = img_height - wm_height

    # Область накладання водяного знака
    region_of_interest = main_image[y_start:y_start + wm_height, x_start:x_start + wm_width]

    # Якщо водяний знак має альфа-канал
    if watermark.shape[2] == 4:
        # Виділяємо альфа-канал
        alpha = watermark[:, :, 3] / 255.0
        watermark_rgb = watermark[:, :, :3]

        # Застосовуємо альфа-канал для накладання
        for channel in range(3):
            region_of_interest[:, :, channel] = (
                alpha * watermark_rgb[:, :, channel] + (1 - alpha) * region_of_interest[:, :, channel]
            )
    else:
        # Накладання без альфа-каналу
        blended = cv2.addWeighted(region_of_interest, 1 - transparency, watermark, transparency, 0)
        main_image[y_start:y_start + wm_height, x_start:x_start + wm_width] = blended

    # Зберігаємо фінальний результат
    cv2.imwrite(output_file, main_image)
    print(f"Водяний знак додано успішно. Результат збережено: {output_file}")

# Приклад виклику функції
source_image = 'PR9/photo.jpeg'  # Вхідне зображення
watermark_image = 'PR9/watermark.jpg'  # Файл водяного знака
output_file = 'PR9/photo_output.jpg'  # Збереження результату
transparency = 0.3  # Прозорість водяного знака (від 0.0 до 1.0)

apply_watermark(source_image, watermark_image, output_file, transparency)
