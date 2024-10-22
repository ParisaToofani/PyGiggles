# -*- coding: utf-8 -*-
"""
Created on Tue Oct  22 2:29:14 2024

@author: Parisa Toofani Movaghar
"""
#-----------------------------------------------------------------------
# Import the required libraries
#==================================
# General Libraries
#==================================
import numpy as np # Library for large, multi-dimensional arrays and matrices
import pandas as pd # Library for data manipulation and analysis
import matplotlib.pyplot as plt # Plotting library
#==================================
# Geo based Libraries
#==================================
import geopandas as gpd # geospatial data manipulation
# cartropy: geospatial data processing in order to produce maps
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from shapely.geometry import Point, Polygon # Library for manipulation and analysis of planar geometric objects
#-----------------------------------------------------------------------
class PolygonDrawer:

    def __init__(self, spatial_lat, spatial_lng):
        self.spatial_lat = spatial_lat # user's latitude array
        self.spatial_lng = spatial_lng # user's longitude array
        self.all_polygons = [] # storing all the polygones drawn by the user
        self.polygon_points = []  # storing polygon positions (lat/lng)
        self.drawn_elements = []  # storing the elements drawn by the users
        self.coord_text = None  # displaying polygon lat/lng real time
        self.fig, self.ax = plt.subplots()  # create figure and axis
        self.setup_plot() # setting up the plot

    def setup_plot(self):
        """
        Setting up the plots creation
        This is used in the initalization of the class to setup the
        basis of the canvas for plotting
        >>> Please look at __init__ function at self.setup_plot()

        Parameters
        ----------
        N/A

        Returns
        -------
        N/A

        Sources:
        --------
        1. https://scitools.org.uk/cartopy/docs/v0.14/matplotlib/feature_interface.html
        2. https://matplotlib.org/stable/users/explain/figure/event_handling.html

        Examples
        --------
        N/A

        """
        # Create axis + projection to Plate Carree
        # > Info| Plate Carree is a map projection that uses a grid of parallels 
        # and meridians to create squares 
        # that stretch from pole to pole and east to west
        self.ax = plt.axes(projection=ccrs.PlateCarree())
        self.ax.set_aspect('equal', adjustable='datalim') # setting equal aspect ratio to the plot
        self.ax.set_title("Left-click to create polygon, \
                          right-click to finish, \
                          double-click to clear points") # Info on how to work with Polygones
        # Plot the base grid points
        self.ax.scatter(self.spatial_lat, # Enter latitude array
                        self.spatial_lng, # Enter longitude array
                        s=1.0, c='k', transform=ccrs.PlateCarree() # Setting up the styles
                        )  
        # Applying world map options
        # Src: https://scitools.org.uk/cartopy/docs/v0.14/matplotlib/feature_interface.html
        # Sample of description grabbed from the website:
        # ----------------------------------------------
        # Name	                    Description
        # ----------------------------------------------
        # cartopy.feature.BORDERS     Country boundaries.
        # cartopy.feature.COASTLINE   Coastline, including major islands.
        # cartopy.feature.LAKES       Natural and artificial lakes.
        # cartopy.feature.LAND        Land polygons, including major islands.
        # cartopy.feature.OCEAN       Ocean polygons.
        # cartopy.feature.RIVERS      Single-line drainages, including lake centerlines.
        # ----------------------------------------------
        self.ax.add_feature(cfeature.LAND, facecolor='lightgray')
        self.ax.add_feature(cfeature.BORDERS, facecolor='k')
        self.ax.add_feature(cfeature.COASTLINE, facecolor='brown')
        self.ax.add_feature(cfeature.STATES, edgecolor='brown')
        self.ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        self.ax.add_feature(cfeature.LAKES, facecolor='lightblue')
        self.ax.add_feature(cfeature.RIVERS, facecolor='lightblue')
        # Load Natural Earth data for US state boundaries
        shapefile_path = shpreader.natural_earth(resolution='110m', 
                                                 category='cultural', 
                                                 name='admin_1_states_provinces_lakes')
        reader = shpreader.Reader(shapefile_path)
        # Iterate through each state geometry and plot its name at its centroid
        for state in reader.records():
            if state.attributes['admin'] == 'United States of America': # Get the states/province within required country (here United States)
                state_name = state.attributes['name'] # States name
                centroid = state.geometry.centroid # States centroids within the Poly region
                # !!! As you are in specific system projection, please do not forget to transform the data
                self.ax.text(centroid.x, centroid.y, 
                             state_name, fontsize=12, 
                             ha='center', transform=ccrs.PlateCarree()) # Add the state name at the centroid position
        self.ax.gridlines(draw_labels=True, 
                          dms=True, 
                          x_inline=False, 
                          y_inline=False) # Add gridlines and labels
        # Call to the on_click function --> using the matplotlib canvas method
        # to perform click aware plotting 
        self.fig.canvas.mpl_connect('button_press_event', self.on_click) # Connect the click event to the on_click handler
    

    def on_click(self, event):
        """
        Handling the event (here the mouse click by the user on the plot)

        Parameters
        ----------
        event: Type of the mouse click on the screen by the user such as:
        1. Double click
        2. Right click
        3. Left click

        Returns
        -------
        Actions based on the click type

        Sources:
        --------
        N/A

        Examples
        --------
        N/A
      
        """
        # The figure manager is a container for the actual 
        # backend-depended window that displays the figure on screen.
        toolbar = plt.get_current_fig_manager().toolbar
        if toolbar.mode != '' and toolbar.mode in ['zoom rect', 'pan/zoom']:
            return  # Ignore clicks if in zoom/pan mode

        # Handle double-click to clear points and lines
        if event.dblclick:
            self.clear_polygon()
            return

        # Handle left-click to add points
        if event.button == 1:  # Left-click
            self.add_point(event)

        # Handle right-click to finish polygon
        elif event.button == 3:  # Right-click to finish
            self.finish_polygon()

    def add_point(self, event):
        """Add a point to the polygon."""
        # Append the lat/lng coordinates
        self.polygon_points.append([event.xdata, event.ydata])  # Store point
        
        # Plot the point on the graph
        point = self.ax.plot(event.xdata, event.ydata, 'ro')
        self.drawn_elements.append(point[0])  # Save reference to the point

        # Update and display the coordinates
        if self.coord_text:
            self.coord_text.remove()  # Remove previous coordinate text

        # self.coord_text = self.ax.text(event.xdata, event.ydata, f'({event.xdata:.4f}, {event.ydata:.4f})',
        #                                fontsize=9, color='blue')
        # self.drawn_elements.append(self.coord_text)  # Save reference to the coordinate text

        plt.draw()  # Redraw the plot

    def finish_polygon(self):
        """Finish the polygon by connecting the first and last points."""
        if len(self.polygon_points) < 3:
            print("Need at least 3 points to form a polygon.")
            return

        # Close the polygon by connecting the first and last points
        self.polygon_points.append(self.polygon_points[0])
        
        # Plot the polygon line
        line = self.ax.plot(*zip(*self.polygon_points), 'g-')  # Draw polygon line
        self.drawn_elements.append(line[0])  # Save reference to the line

        plt.draw()  # Redraw the plot
        print("Polygon finished.")
        self.all_polygons.append(self.get_polygon_points())

    def clear_polygon(self):
        print('Hi')
        """Clear all drawn points and lines."""
        for elem in self.drawn_elements:
            elem.remove()  # Remove points and lines
        self.drawn_elements.clear()  # Clear the list of drawn elements
        self.polygon_points.clear()  # Clear the list of polygon points

        plt.draw()  # Redraw the plot to reflect the cleared elements
        print("Polygon cleared.")

    def get_polygon_points(self):
        """Get the points of the drawn polygon as a NumPy array."""
        return np.array(self.polygon_points) if self.polygon_points else None