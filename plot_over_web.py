import matplotlib.pyplot as plt
import numpy as np
import json
import skrf as rf
import seaborn as sns

class ChartPlotter:
    def __init__(self, config_json):
        self.config = json.loads(config_json)
        self.rows = self.config['layout']['rows']
        self.columns = self.config['layout']['columns']
        self.figsize = self.config['layout'].get('figsize', (10, 8))
        self.fig, self.axs = plt.subplots(self.rows, self.columns, figsize=self.figsize)


        if self.rows == 1 and self.columns == 1:
            self.axs = np.array([[self.axs]])
        elif self.rows == 1:
            self.axs = np.expand_dims(self.axs, axis=0)
        elif self.columns == 1:
            self.axs = np.expand_dims(self.axs, axis=1)
        elif self.rows == 0 or self.columns == 0:
            raise ValueError("Die Anzahl der Reihen und Spalten muss mindestens 1 betragen.")
        
        self.validate_config()

    def validate_config(self):

        layout = self.config.get('layout', {})
        if 'rows' not in layout or 'columns' not in layout:
            raise ValueError("Fehlende 'rows' oder 'columns' in der Layout-Konfiguration.")
        if layout['rows'] < 1 or layout['columns'] < 1:
            raise ValueError("'rows' und 'columns' müssen mindestens 1 sein.")


        figsize = layout.get('figsize', None)
        if figsize:
            if not isinstance(figsize, list) or len(figsize) != 2:
                raise ValueError("'figsize' muss eine Liste mit zwei Werten sein.")
            if not all(isinstance(x, (int, float)) for x in figsize):
                raise ValueError("Die Werte in 'figsize' müssen Zahlen sein.")


        charts = self.config.get('charts', [])
        if not isinstance(charts, list):
            raise ValueError("'charts' muss eine Liste sein.")

        if len(charts) == 0:
            raise ValueError("Es müssen mindestens 1 Diagramm definiert sein.")

        if len(charts) > self.rows * self.columns:
            raise ValueError("Mehr Diagramme als Platz in der Layout-Konfiguration.")
        
        for chart in charts:
            chart_type = chart.get('type', None)
            if chart_type not in ['line', 'multi_line', 'bar', 'scatter', 'smith', 'hist', 'heatmap', 'pie']:
                raise ValueError(f"Unbekannter Diagrammtyp: {chart_type}")

            data = chart.get('data', {})
            options = chart.get('options', {})
            
            if chart_type in ['line', 'scatter']:
                if 'x' not in data or 'y' not in data:
                    raise ValueError(f"Fehlende 'x' oder 'y' in den Daten für Diagrammtyp '{chart_type}'.")
                if not isinstance(data['x'], list) or not isinstance(data['y'], list):
                    raise ValueError("Die 'x'- und 'y'-Daten müssen Listen sein.")
            
            if chart_type == 'multi_line':
                if 'lines' not in data:
                    raise ValueError("Fehlende 'lines' in den Daten für Diagrammtyp 'multi_line'.")
                if not isinstance(data['lines'], list):
                    raise ValueError("'lines' muss eine Liste von Linienkonfigurationen sein.")
                for line in data['lines']:
                    if 'x' not in line or 'y' not in line:
                        raise ValueError("Jede Linie muss 'x' und 'y' in den Daten haben.")
                    if not isinstance(line['x'], list) or not isinstance(line['y'], list):
                        raise ValueError("Die 'x'- und 'y'-Daten für jede Linie müssen Listen sein.")

            if chart_type == 'smith':
                if 'real' not in data or 'imag' not in data:
                    raise ValueError("Fehlende 'real' oder 'imag' in den Daten für Diagrammtyp 'smith'.")
                if not isinstance(data['real'], list) or not isinstance(data['imag'], list):
                    raise ValueError("Die 'real'- und 'imag'-Daten müssen Listen sein.")
            
            if chart_type == 'heatmap':
                if 'matrix' not in data:
                    raise ValueError("Fehlende 'matrix' in den Daten für Diagrammtyp 'heatmap'.")
                if not isinstance(data['matrix'], list) or not all(isinstance(row, list) for row in data['matrix']):
                    raise ValueError("Die 'matrix'-Daten müssen eine Liste von Listen sein.")
                if 'x_labels' in data and (not isinstance(data['x_labels'], list) or len(data['x_labels']) != len(data['matrix'][0])):
                    raise ValueError("'x_labels' muss eine Liste sein, deren Länge der Anzahl der Spalten in 'matrix' entspricht.")
                if 'y_labels' in data and (not isinstance(data['y_labels'], list) or len(data['y_labels']) != len(data['matrix'])):
                    raise ValueError("'y_labels' muss eine Liste sein, deren Länge der Anzahl der Zeilen in 'matrix' entspricht.")
            
            if chart_type == 'pie':
                if 'labels' not in data or 'sizes' not in data:
                    raise ValueError("Fehlende 'labels' oder 'sizes' in den Daten für Diagrammtyp 'pie'.")
                if not isinstance(data['labels'], list) or not isinstance(data['sizes'], list):
                    raise ValueError("Die 'labels'- und 'sizes'-Daten müssen Listen sein.")
                if len(data['labels']) != len(data['sizes']):
                    raise ValueError("'labels' und 'sizes' müssen dieselbe Länge haben.")
    
    def plot_charts(self):
        for i, chart in enumerate(self.config['charts']):
            # Berechne den Index für das 2D-Array
            row_idx = i // self.columns
            col_idx = i % self.columns
            ax = self.axs[row_idx, col_idx]

            self.plot_chart(ax, chart)

        plt.tight_layout()
        plt.show()

    def plot_chart(self, ax, chart):
        chart_type = chart['type']
        options = chart['options']

        if chart_type == 'line':
            x = chart['data']['x']
            y = chart['data']['y']
            ax.plot(x, y, color=options['style'].get('color', 'blue'), 
                         linestyle=options['style'].get('linestyle', '-'), 
                         marker=options['style'].get('marker', ''),
                         label=options['legend'].get('label', ''))
        elif chart_type == 'multi_line':
            for line in chart['data']['lines']:
                x = line['x']
                y = line['y']
                style = line['style']
                ax.plot(x, y, color=style.get('color', 'blue'), 
                         linestyle=style.get('linestyle', '-'), 
                         marker=style.get('marker', ''),
                         label=line.get('label', ''))
        elif chart_type == 'bar':
            x = chart['data']['x']
            y = chart['data']['y']
            ax.bar(x, y, color=options['style'].get('color', 'blue'))
        elif chart_type == 'scatter':
            x = chart['data']['x']
            y = chart['data']['y']
            ax.scatter(x, y, color=options['style'].get('color', 'blue'), 
                             marker=options['style'].get('marker', 'o'))
        elif chart_type == 'smith':
            real = chart['data']['real']
            imag = chart['data']['imag']
            z = np.array(real) + 1j*np.array(imag)
            smith_chart = rf.Network(s=z, frequency=rf.Frequency(1, 1, len(z)))
            smith_chart.plot_s_smith(ax=ax, show_legend=options['legend']['show'])
            ax.set_xlabel(options.get('xlabel', 'Realteil'))
            ax.set_ylabel(options.get('ylabel', 'Imaginärteil'))
        elif chart_type == 'hist':
            data = chart['data']['values']
            ax.hist(data, bins=options['style'].get('bins', 10), color=options['style'].get('color', 'blue'))
        elif chart_type == 'heatmap':
            matrix = chart['data']['matrix']
            x_labels = chart['data'].get('x_labels', [])
            y_labels = chart['data'].get('y_labels', [])
            sns.heatmap(matrix, ax=ax, cmap=options['style'].get('cmap', 'viridis'), 
                        xticklabels=x_labels, yticklabels=y_labels, 
                        cbar=options['style'].get('colorbar', True))
            ax.set_title(options['title'])
            ax.set_xlabel(options.get('xlabel', ''))
            ax.set_ylabel(options.get('ylabel', ''))
        elif chart_type == 'pie':
            labels = chart['data']['labels']
            sizes = chart['data']['sizes']
            ax.pie(sizes, labels=labels, colors=options['style'].get('colors', None),
                   autopct='%1.1f%%', startangle=90)
            ax.set_title(options['title'])


        #generische optionen
        ax.set_title(options.get('title', ''))
        if 'xlabel' in options:
            ax.set_xlabel(options['xlabel'])
        if 'ylabel' in options:
            ax.set_ylabel(options['ylabel'])


        for annotation in options.get('annotations', []):
            ax.annotate(annotation['text'], xy=annotation['xy'], xytext=annotation['xytext'], 
                        arrowprops=annotation['arrowprops'])
        

        if 'legend' in options and options['legend'].get('show', False):
            ax.legend(loc=options['legend'].get('location', 'best'))


        if options.get('grid', False):
            ax.grid(True)


        if 'xlim' in options:
            ax.set_xlim(options['xlim'])
        if 'ylim' in options:
            ax.set_ylim(options['ylim'])
        if 'xticks' in options:
            ax.set_xticks(options['xticks'])
        if 'yticks' in options:
            ax.set_yticks(options['yticks'])




json_data = '''{
  "layout": {
    "rows": 3,
    "columns": 3,
    "figsize": [12, 12]
  },
  "charts": [
    {
      "type": "line",
      "data": {
        "x": [1, 2, 3, 4, 5],
        "y": [2, 3, 5, 7, 11]
      },
      "options": {
        "title": "Liniendiagramm",
        "xlabel": "X-Achse",
        "ylabel": "Y-Achse",
        "style": {
          "color": "blue",
          "linestyle": "-",
          "marker": "o"
        },
        "legend": {
          "show": true,
          "label": "Linie 1",
          "location": "upper left"
        },
        "annotations": []
      }
    },
    {
      "type": "multi_line",
      "data": {
        "lines": [
          {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 3, 5, 7, 11],
            "style": {
              "color": "blue",
              "linestyle": "-",
              "marker": "o"
            },
            "label": "Linie 1"
          },
          {
            "x": [1, 2, 3, 4, 5],
            "y": [1, 2, 4, 8, 16],
            "style": {
              "color": "red",
              "linestyle": "--",
              "marker": "s"
            },
            "label": "Linie 2"
          }
        ]
      },
      "options": {
        "title": "Mehrere Linien",
        "xlabel": "X-Achse",
        "ylabel": "Y-Achse",
        "style": {},
        "legend": {
          "show": true,
          "location": "upper left"
        },
        "annotations": []
      }
    },
    {
      "type": "bar",
      "data": {
        "x": ["A", "B", "C", "D"],
        "y": [5, 7, 3, 8]
      },
      "options": {
        "title": "Balkendiagramm",
        "xlabel": "Kategorien",
        "ylabel": "Werte",
        "style": {
          "color": ["red", "green", "blue", "orange"]
        },
        "legend": {
          "show": false
        },
        "annotations": []
      }
    },
    {
      "type": "scatter",
      "data": {
        "x": [1, 2, 3, 4, 5],
        "y": [5, 6, 2, 4, 7]
      },
      "options": {
        "title": "Streudiagramm",
        "xlabel": "X-Achse",
        "ylabel": "Y-Achse",
        "grid": true,
        "style": {
          "color": "green",
          "marker": "x"
        },
        "legend": {
          "show": false
        },
        "annotations": []
      }
    },
    {
      "type": "smith",
      "data": {
        "real": [0.2, 0.5, 0.7, 1.0],
        "imag": [0.1, 0.3, 0.4, 0.6]
      },
      "options": {
        "title": "Smith Chart",
        "xlabel": "Realteil",
        "ylabel": "Imaginärteil",
        "style": {
          "color": "black",
          "marker": "x"
        },
        "legend": {
          "show": false
        },
        "annotations": []
      }
    },
    {
      "type": "hist",
      "data": {
        "values": [1, 2, 2, 3, 3, 3, 4, 4, 5]
      },
      "options": {
        "title": "Histogramm",
        "xlabel": "Wert",
        "ylabel": "Häufigkeit",
        "style": {
          "color": "purple",
          "bins": 5
        },
        "legend": {
          "show": false
        },
        "annotations": []
      }
    },
    {
      "type": "heatmap",
      "data": {
        "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        "x_labels": ["A", "B", "C"],
        "y_labels": ["1", "2", "3"]
      },
      "options": {
        "title": "Heatmap",
        "xlabel": "X-Achse",
        "ylabel": "Y-Achse",
        "style": {
          "cmap": "viridis",
          "colorbar": true
        },
        "annotations": []
      }
    },
    {
      "type": "pie",
      "data": {
        "labels": ["A", "B", "C"],
        "sizes": [10, 20, 30]
      },
      "options": {
        "title": "Kreisdiagramm",
        "style": {
          "colors": ["red", "green", "blue"]
        },
        "legend": {
          "show": true
        },
        "annotations": []
      }
    }
  ]
}
'''


plotter = ChartPlotter(json_data)
plotter.plot_charts()

