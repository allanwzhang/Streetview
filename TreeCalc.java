
public class TreeCalc {
	double[] xy;
	double imageX;
	
	public static void main(String[] args) {
		double focal = 320 / Math.tan(Math.toRadians(78/2));
		
		System.out.println("Predicted focal length: " + focal + " pixels");
		
		TreeCalc t = new TreeCalc(40.85400024006033, -73.93127653545221, 40.85395873, -73.93134041, 208.0, focal);
		System.out.println("Z: " + t.xy[0] + " X: " + t.xy[1]);
		System.out.println("Predicted imageX length: " + t.imageX + " pixels");
	}
	
	public TreeCalc(double clat, double clong, double tlat, double tlong, double heading, double focal) {
		Deg2UTM c = new Deg2UTM(clat, clong);
		Deg2UTM t = new Deg2UTM(tlat, tlong);
//		System.out.println(c.Easting + " " + c.Northing);
//		System.out.println(t.Easting + " " + t.Northing);
		t.Easting -= c.Easting;
		t.Northing -= c.Northing;
		c.Easting = 0;
		c.Northing = 0;
		System.out.println("Relative x, y for tree: " + t.Easting + " " + t.Northing);
		//yc = mcx + bc
		//yt = mtx + bt
		if(heading > 180) heading -= 180;
		double mc = Math.tan(Math.toRadians(90 - heading));
		double bc = 0;
		double mt = -1 * 1/mc;
		double bt = t.Northing - mt * t.Easting;
		double crossX = (bt - bc) / (mc - mt);
		double crossY = mc * crossX;
		System.out.println("Intersection point: " + crossX + " " + crossY);
		xy = new double[] {dist(crossX, crossY, 0, 0), dist(crossX, crossY, t.Easting, t.Northing)};
//		pFocal = xy[0] * pixels / xy[1];
		imageX = focal * xy[1] / xy[0];
	}
	
	double dist(double x1, double y1, double x2, double y2) {
		return Math.sqrt(Math.pow(x1-x2, 2) + Math.pow(y1-y2, 2));
	}
}
