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

    def __init__(self, spatial_lat, spatial_lng, poly_text = False):
        self.spatial_lat = spatial_lat # user's latitude array
        self.spatial_lng = spatial_lng # user's longitude array
        self.all_polygons = [] # storing all the polygones drawn by the user
        self.polygon_points = []  # storing polygon positions (lat/lng)
        self.drawn_elements = []  # storing the elements drawn by the users
        self.coord_text = None  # displaying polygon lat/lng real time
        self.show_text = poly_text
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
        1. Double click: deleting polygon
        2. Right click: add points to create a polygone
        3. Left click: complete polygone drawing

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
            # !!! This is necessary to be defined as not mistaken 
            # zooming and panning click with polygone point drawing click
            return  # Ignore clicks if in zoom/pan mode

        # Handle double-click to clear points and lines
        if event.dblclick:
            self.clear_polygon() # when double click delete the drawn polygon
            return # need this to get out of this function after clearing the polygon

        # Handle left-click to add points
        if event.button == 1:  # Left-click
            self.add_point(event) # Draw a point

        # Handle right-click to finish polygon
        elif event.button == 3:  # Right-click to finish
            self.finish_polygon() # Finish the polygon 

    def add_point(self, event):
        """
        Drawing points on the click event to create a polygon

        Parameters
        ----------
        event: Type of the mouse click on the screen by the user such as:
        1. Double click: deleting polygon
        2. Right click: add points to create a polygone
        3. Left click: complete polygone drawing

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
        # Append the lat/lng coordinates
        # here event.xdata and .ydata return to point coordinates 
        # (for instance latitude and longitude)
        self.polygon_points.append([event.xdata, event.ydata])  # Store point used for creating polygon
        
        point = self.ax.plot(event.xdata, event.ydata, 'ro') # Plot the point on the graph
        self.drawn_elements.append(point[0])  # Save reference to the point, plotting elements

        # Update and display the coordinates
        if self.coord_text:
            self.coord_text.remove()  # Remove previous coordinate text

        if self.show_text: # make based on user decision to if shows the point coordinate real time or not
            self.coord_text = self.ax.text(event.xdata, event.ydata, 
                                           f'({event.xdata:.4f}, {event.ydata:.4f})',
                                           fontsize=9, color='blue')
            self.drawn_elements.append(self.coord_text)  # Save reference to the coordinate text

        plt.draw()  # Redraw the plot

    def finish_polygon(self):
        """
        Finish the polygon by connecting the first and last points.

        Parameters
        ----------
        N/A

        Returns
        -------
        N/A

        Sources:
        --------
        N/A

        Examples
        --------
        N/A
        """
        if len(self.polygon_points) < 3: # Check if there is enough points to create a polygon
            print("Need at least 3 points to form a polygon.")
            return

        self.polygon_points.append(self.polygon_points[0]) # Close the polygon by connecting the first and last points
        
        # Plot the polygon line
        # !!! the lines are created based on the points order placement
        line = self.ax.plot(*zip(*self.polygon_points), 'g-')  # Draw polygon line 
        self.drawn_elements.append(line[0])  # Save reference to the line

        plt.draw()  # Redraw the plot
        print("Polygon finished.") 
        # get all points of polygon (further can be used for post processing)
        self.all_polygons.append(self.get_polygon_points()) 

    def clear_polygon(self):
        """
        Clear all drawn points and lines.
        
        Parameters
        ----------
        N/A

        Returns
        -------
        N/A

        Sources:
        --------
        N/A

        Examples
        --------
        N/A
        """
        for elem in self.drawn_elements: # Iterate over all previously saved elements
            elem.remove()  # Remove elements (points and lines)
        self.drawn_elements.clear()  # Clear the list of drawn elements
        self.polygon_points.clear()  # Clear the list of polygon points

        plt.draw()  # Redraw the plot to reflect the cleared elements
        print("Polygon cleared.")

    def get_polygon_points(self):
        """
        Get the points of the drawn polygon as a NumPy array.
        
        Parameters
        ----------
        N/A (inside uses the polygon points)

        Returns
        -------
        All extracted polygon points

        Sources:
        --------
        N/A

        Examples
        --------
        N/A
        """
        return np.array(self.polygon_points) if self.polygon_points else None