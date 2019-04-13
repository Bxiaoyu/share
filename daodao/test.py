from werkzeug.security import generate_password_hash, check_password_hash


password = generate_password_hash('541086sky')
print(password)