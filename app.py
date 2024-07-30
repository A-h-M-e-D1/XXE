from flask import Flask, request, jsonify, Response, render_template
from lxml import etree

app = Flask(__name__)

books = []

@app.route('/books', methods=['GET'])
def get_book():
    root = etree.Element('root')
    for book in books:
        book_elem = etree.Element('book')
        title_elem = etree.Element('title')
        title_elem.text = book['title']
        author_elem = etree.Element('author')
        author_elem.text = book['author']
        book_elem.append(title_elem)
        book_elem.append(author_elem)
        root.append(book_elem)

    return Response(etree.tostring(root, pretty_print=True), mimetype='application/xml')

@app.route('/add', methods=['POST'])
def add_book():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and file.filename.endswith('.xml'):
        try:
          
            parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
            tree = etree.parse(file, parser)
            root = tree.getroot()
            
            external_content = ""
            for book_elem in root.findall('book'):
                title = book_elem.find('title').text
                author = book_elem.find('author').text
                if title:
                    external_content += f"{title}\n"
                book = {
                    'title': title,
                    'author': author
                }
                books.append(book)
            
            return jsonify({
                'message': 'Books added successfully',
                'external_content': external_content
            }), 201
        except etree.XMLSyntaxError:
            return jsonify({'message': 'Invalid XML'}), 400
    else:
        return jsonify({'message': 'File type not allowed'}), 400

@app.route('/')
def upload_form():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
