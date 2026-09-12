import 'package:flutter/material.dart';

class SetupRequiredScreen extends StatelessWidget {
  const SetupRequiredScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Icon(Icons.settings_suggest_outlined, size: 64),
              SizedBox(height: 16),
              Text(
                'Firebase no esta configurado',
                style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 12),
              Text(
                'Revisa lib/firebase_options.dart y vuelve a compilar '
                'con flutter run.',
              ),
            ],
          ),
        ),
      ),
    );
  }
}
