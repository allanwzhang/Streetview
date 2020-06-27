
public class TreeCalc {
	double[] xy;
	double imageY;
	
	public TreeCalc(double clat, double clong, double tlat, double tlong, double heading) {
		Deg2UTM c = new Deg2UTM(clat, clong);
		Deg2UTM t = new Deg2UTM(tlat, tlong);
		t.Easting -= c.Easting;
		t.Northing -= c.Northing;
		c.Easting = 0;
		c.Northing = 0;
		System.out.println(t.Easting + " " + t.Northing);
		//yc = mcx + bc
		//yt = mtx + bt
		if(heading > 180) heading -= 180;
		double mc = Math.tan(Math.toRadians(90 - heading));
		double bc = 0;
		double mt = -1 * 1/mc;
		double bt = t.Northing - mt * t.Easting;
		double crossX = (bt - bc) / (mc - mt);
		double crossY = mc * crossX;
		xy = new double[] {dist(crossX, crossY, 0, 0), dist(crossX, crossY, t.Easting, t.Northing)};
		imageY = 5.1 * xy[1] / xy[0];  
	}
	
	double dist(double x1, double y1, double x2, double y2) {
		return Math.sqrt(Math.pow(x1-x2, 2) + Math.pow(y1-y2, 2));
	}
}
