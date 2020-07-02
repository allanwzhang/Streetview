import java.io.*;
import java.util.*;
import java.net.*;
import java.nio.file.*;

public class streetview {
	static double totalImages = 0;
	
	public static void main(String[] args) throws IOException {
		BufferedReader f = new BufferedReader(new FileReader("Centerline.csv"));
		PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter("Metadata.txt")));
		
		TreeMap<String, ArrayList<Street>> streets = parseData(f);
		findHeading(streets);
		
		System.out.println("Time: " + System.currentTimeMillis());
		for(String key : streets.keySet()) {
			System.out.println(key);
		}
		
		System.out.println("Give me a street from the list");
		Scanner sc = new Scanner(System.in);
		String input = sc.nextLine().toUpperCase();
		while(!streets.containsKey(input)) {
			System.out.println("That isn't a valid street");
			System.out.println("Please give me one from the list");
			input = sc.nextLine();
		}
		for(Street curr : streets.get(input)) {
			System.out.println(curr);
			callAPI(curr, out);
		}
		
		System.out.println(totalImages);
		
		sc.close();
		out.close();
		f.close();
	}
	
	static void callAPI(Street s, PrintWriter out) throws IOException {	
		for(int i = 0; i < s.points.size(); i++) {
			double[] curr = s.points.get(i);
			String url = "https://maps.googleapis.com/maps/api/streetview?size=640x640&location=" + curr[0] + "," + curr[1] + 
						 "&fov=" + s.fov + "&heading=" + curr[2] + "&pitch=0&source=outdoor&key=AIzaSyCi7VDbFboRwENnMCmE2LuEf5kyuwEnBwU";
			try(InputStream in = new URL(url).openStream()){
			    Files.copy(in, Paths.get("C:/Allan/Streetview/" + s.name.replace(' ', '_') + "_s1_" + totalImages + ".jpg"));
			}
			out.println(s.name.replace(' ', '_') + "_s1_" + totalImages + ".jpg");
			out.println(url);
			url = "https://maps.googleapis.com/maps/api/streetview?size=640x640&location=" + curr[0] + "," + curr[1] + 
				  "&fov=" + s.fov + "&heading=" + (curr[2] + 180) + "&pitch=0&key=AIzaSyCi7VDbFboRwENnMCmE2LuEf5kyuwEnBwU";
			try(InputStream in = new URL(url).openStream()){
				Files.copy(in, Paths.get("C:/Allan/Streetview/" + s.name.replace(' ', '_')  + "_s2_"+ (totalImages + 1) + ".jpg"));
			}
			out.println(s.name.replace(' ', '_') + "_s2_" + (totalImages + 1) + ".jpg");
			out.println(url);
			totalImages += 2;
		}
		
	}
	
	static TreeMap<String, ArrayList<Street>> parseData(BufferedReader f) throws IOException {
		TreeMap<String, ArrayList<Street>> streets = new TreeMap<>();
		f.readLine();
		System.out.println("Time: " + System.currentTimeMillis());
		while(f.ready()) {
			ArrayList<String> curr = split(f.readLine());
			int type = Integer.parseInt(curr.get(18));
			if(type != 1 || Integer.parseInt(curr.get(14)) == 0 || Integer.parseInt(curr.get(13)) != 1) continue;
			Street toAdd = new Street(findPoints(curr.get(3)), removeEW(curr.get(10)), Integer.parseInt(curr.get(14)) / 3.281);
			toAdd.avDist = findAvDist(toAdd.points);
			toAdd.fov = calculateFOV(toAdd);
			while(toAdd.fov > 60) {
				doublePoints(toAdd.points);
				toAdd.avDist = findAvDist(toAdd.points);
				toAdd.fov = calculateFOV(toAdd);
			}
			if(streets.containsKey(toAdd.name)) {
				streets.get(toAdd.name).add(toAdd);
			} else {
				ArrayList<Street> newStreet = new ArrayList<>();
				newStreet.add(toAdd);
				streets.put(toAdd.name, newStreet);
			}
		}
		System.out.println("Time: " + System.currentTimeMillis());
		return streets;
	}
	
	static String removeEW(String name) {
		if(name.split(" ").length < 2) return name;
		if(name.split(" ")[0].equals("E") || name.split(" ")[0].equals("W")) return name.substring(2);
		return name;
	}
	
	static int calculateFOV(Street s) {
		return 2 * (int) Math.toDegrees(Math.atan(s.avDist / (s.width)));
	}
	
	static double findAvDist(ArrayList<double[]> points) {
		double sum = 0;
		for(int i = 1; i < points.size(); i++) {
			sum += FlatEarthDist.distance(points.get(i - 1)[0], points.get(i - 1)[1], points.get(i)[0], points.get(i)[1]);
		}
		return sum / (points.size() - 1);
	}
	
	static void findHeading(TreeMap<String, ArrayList<Street>> streets) {
		for(String key : streets.keySet()) {
			for(Street s : streets.get(key)) {
				for(int i = 1; i < s.points.size(); i++) {
					double[] left = s.points.get(i - 1);
					double[] right = s.points.get(i);
					Deg2UTM leftutm = new Deg2UTM(left[0], left[1]);
					Deg2UTM rightutm = new Deg2UTM(right[0], right[1]);
					double slope = -1 *  (rightutm.Northing - leftutm.Northing) / (rightutm.Easting - leftutm.Easting);
					slope = 1 / slope;
					double degrees = 90 - Math.toDegrees(Math.atan(slope));
					s.points.get(i - 1)[2] = Math.round(degrees);
					s.points.get(i)[2] = Math.round(degrees);
				}
			}
		}
	}
	
	static ArrayList<double[]> findPoints(String s) {
		s = s.substring(19, s.length() - 3);
		String[] sll = s.split(", ");
		ArrayList<double[]> result = new ArrayList<>();
		
		for(int i = 0; i < sll.length; i++) {
			String[] arr = sll[i].split(" ");
			result.add(new double[] {Double.parseDouble(arr[1]), Double.parseDouble(arr[0]), -1});
		}

		return result;
	}

	static void doublePoints(ArrayList<double[]> points) {
		for(int i = 1; i < points.size(); i++) {
			points.add(i, mid(points.get(i - 1)[0], points.get(i - 1)[1], points.get(i)[0], points.get(i)[1]));
			i++;
		}
	}
	
	static double[] mid(double lat1, double lon1, double lat2, double lon2){

	    double dLon = Math.toRadians(lon2 - lon1);

	    //convert to radians
	    lat1 = Math.toRadians(lat1);
	    lat2 = Math.toRadians(lat2);
	    lon1 = Math.toRadians(lon1);

	    double Bx = Math.cos(lat2) * Math.cos(dLon);
	    double By = Math.cos(lat2) * Math.sin(dLon);
	    double lat3 = Math.atan2(Math.sin(lat1) + Math.sin(lat2), Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By));
	    double lon3 = lon1 + Math.atan2(By, Math.cos(lat1) + Bx);

	    return new double[] {Math.toDegrees(lat3), Math.toDegrees(lon3), -1};
	}
	
	static String printURL(Street s, int j) {
		String result = "https://maps.googleapis.com/maps/api/streetview?size=640x640&location=" + s.points.get(j)[0] + ","
						+ s.points.get(j)[1] + "&fov=" + s.fov + "&heading=" + s.points.get(j)[2] + "&pitch=0&source=outdoor&key=AIzaSyCi7VDbFboRwENnMCmE2LuEf5kyuwEnBwU";
		return result;
	}
	
	static ArrayList<String> split(String s) {
		ArrayList<String> result = new ArrayList<>();
		char[] arr = s.toCharArray();
		int prev = 0;
		boolean isGeom = false;
		for(int i = 0; i < arr.length; i++) {
			if(arr[i] == '(') isGeom = true;
			if(arr[i] == ')') isGeom = false;
			if(isGeom) continue;
			if(arr[i] == ',') {
				result.add(s.substring(prev, i));
				prev = i + 1;
			}
		}
		result.add(s.substring(prev));
		return result;
	}
}
