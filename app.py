#! /usr/bin/env python3
import ply3d.sensor_view as sv

if __name__ == '__main__':
    sv.app.run_server(host='localhost', port=5000, debug=True,
                      threaded=True)
