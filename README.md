# klima
Get interactive climate diagramm with data from dwd using plotly and flask

# input
input.txt contains location, start date and end date for the diagramm.

# docker cmd
docker build -t klima_flask .
docker run -p 5000:5000 -it --rm --name klima klima_flask

Get IP:
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' klima