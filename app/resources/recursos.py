from fastapi import HTTPException, status


# Contenido HTML para una página web simple
contenido_html = f""" 
        <h1>BOOKING UTEM</h1>
        <h2>Para ingresar, registrese con su cuenta utem</h2>
        <button onClick='fetch("http://127.0.0.1:5000/v1/login")'>
                LOGIN
                </button>
        <br></br>
        <button onClick='fetch("http://localhost:5000/v1/protected")'>
                Protected (Solo si tienes token)
                </button>
        <br></br>
        """

#HTTP Exeptions
HTTP_400_BAD_REQUEST = HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede realizar la reserva debido a la capacidad máxima de la sala"
                )

HTTP_401_UNAUTHORIZED = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

HTTP_500_INTERNAL_SERVER_ERROR = HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al conectar con la base de datos"
        )