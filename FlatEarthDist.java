public class FlatEarthDist {
    //returns distance in meters
    public static double distance(double lat1, double lng1, 
                                      double lat2, double lng2){
     double a = (lat1-lat2)*FlatEarthDist.distPerLat(lat1);
     double b = (lng1-lng2)*FlatEarthDist.distPerLng(lat1);
     return Math.sqrt(a*a+b*b);
    }

    private static double distPerLng(double lat){
      return 0.0003121092*Math.pow(lat, 4)
             +0.0101182384*Math.pow(lat, 3)
                 -17.2385140059*lat*lat
             +5.5485277537*lat+111301.967182595;
    }

    private static double distPerLat(double lat){
            return -0.000000487305676*Math.pow(lat, 4)
                -0.0033668574*Math.pow(lat, 3)
                +0.4601181791*lat*lat
                -1.4558127346*lat+110579.25662316;
    }
}