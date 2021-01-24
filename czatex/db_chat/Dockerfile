FROM mysql:5.7

# Sets the working directory for following COPY and CMD instructions
# Notice we haven’t created a directory by this name - this instruction 
# creates a directory with this name if it doesn’t exist
WORKDIR /app
COPY plik.sql /app
CMD mysql -u root < plik.sql
