
from flask import Flask
import os

def create_app():
	app = Flask(__name__, static_folder='static', template_folder='templates')

	# Blueprint登録
	from routes.views import views_bp
	app.register_blueprint(views_bp)

	return app

if __name__ == '__main__':
	app = create_app()
	app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
